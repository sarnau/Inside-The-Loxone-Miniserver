# Loxone Link NAT protocol

To overcome the limitations of the legacy protocol, the NAT protocol was introduced. It uses the previously unused device type `0` as identification. An extension only supports either the Legacy protocol or the NAT protocol, neither both. The NAT protocol was also cleaned up, with a lot of extension/device specific commands removed and instead using simple "digital value" and "analog value" commands to send value updates.

The following extensions are using the NAT protocol:
- Loxone Tree Extension
- Loxone Internorm Extension
- Loxone DI/AI/AO Extensions
- all Tree devices behind a Tree extensions

The CAN object identifier is 29 bits long and follows a simply scheme for the NAT extensions:

    10000.0dDlnnnn.nnnn0000.cccccccc

- `cccccccc` contains the command byte.
- `nnnnnnnn` is the NAT (`0x01…0x7E`), which is the id of the extension on the Loxone Link bus. A NAT of `0xFF` is a broadcast to all extensions. Bit 7 is set for parked extensions, which have been detected by the Miniserver, but are not configured in Loxone Config.
- `dd` is a direction/type of the command: `00` = sent from a extension/device, `10` = from a extension/device, when sending a shortcut messages back to the Miniserver, `11` = sent from the Miniserver
- `l` package type: `0` = regular package, `1` = fragmented package

This frees up the first byte in the 8 byte data package. This byte is now used for a device ID. This allows to run many devices behind the an extension. This is e.g. used by the Tree Extension. `0xFF` is again used to broadcast to all devices behind an extension. The DI Extension doesn't have devices behind it, in this case the device ID is `0x00`.

Fragmented packages share the same commands with simple packages. This is different to the legacy protocol, where fragmented packages have their own unique commands and actually makes it a bit simpler.

## NAT - network address translation

The NATs are a replacement for the serial number of the extension/device to allow the Miniserver to send messages to a specific extension or device. There are two NATs: one for Loxone Link extensions and one for devices behind a NAT extension, like the Tree Base Extension. The NAT are a single bytes, which can have the following values:

Extension NATs:
- `0x00` - reserved and unused
- `0x01…0x7E` - regular NAT 
- `0x7F` - reserved, because `0x7F` parked would be `0xFF`, which is used for broadcast
- `0x80` - reserved
- `0x81…0xFE` - NAT with bit 7 set defines the extension to be parked (it has not been added in the Loxone Config file)
- `0xFF` - broadcast to all extensions


## Tree Base Extension [tbe]

The Tree Base Extension is a gateway from Loxone Link to two Tree branches. This allows isolating two branches, which can be used for increased security, because devices on one Tree branch never see commands from devices on other Tree branches. Useful to isolate e.g. devices which are outside of the building and could allow listening and/or controlling devices on the bus. Multiple Tree Base Extensions on the Loxone Link are also possible.

The Loxone Tree Extension uses two additional independent CAN 2.0B busses (driven by two MCP2515 CAN controllers), but are clocked at 50kHz (which allows up to 1km of cable length). There is also a minimal change in the address of Tree devices vs. extensions, but the protocol is otherwise identical, instead of `0x10` in the top 5 bits of the object identifier for NAT messages on the Loxone Link bus, the value is `0x11` for Tree branches. The Tree Extension has to be at the end of the Tree branches as well.

The Tree Base Extension sends the `CAN Error reply` whenever a the error count on one of the Tree branches changes, but only once per second. If the Tree extension is in the offline state, e.g. after a reboot or on power-on, it sends a `NAT offer request` at a random interval between 1-1.5s. As a special case after a `NAT offer confirm` command, after sending the `Start` command to the Miniserver, it also sends the current CAN Error status for both branches.

The Tree Base Extensions listens to 3 additional commands, besides the device detection commands:

The `CAN Diagnostics` and `CAN Errors` commands contain a field in `val16` to allow defining one of the 3 CAN busses of the Tree Bus Extension:

- 0 = Tree Bus Extension
- 1 = Left Branch
- 2 = Right Branch

The third command is a `WebService Request`, which the Loxone Config application uses to request detailed information about the extension.


### Device NATs on the Tree Bus

The Tree Base Extension adds a second level of NAT translation, which I call device NATs. The device NAT is stored in the first byte of the 8-byte data package, which for NAT devices is therefore always 7 bytes large.

The device NAT allows significantly more devices on the Miniserver overcoming the 126 NAT extension limit. Because the Tree Base Extension supports two Tree branches, it splits the NATs into left or right branches with up to 62 devices per branch.

Possible Device NATs:
- `0x00` - reserved for the Tree Base Extension and send from a device with the "NAT offer request" command, because it doesn't have a device NAT yet.
- `0x01…0x3E` - Right Loxone Tree bus device (62 possible devices)
- `0x3F` - reserved for tree shortcut testing
- `0x40` - reserved, unused
- `0x41…0x7E` - Left Loxone Tree bus device (62 possible devices)
- `0x7F` - reserved for tree shortcut testing, because `0x7F` parked would be `0xFF`, which is used for broadcast
- `0x80` - reserved, unused
- `0x81…0xBE` - Parked right Loxone Tree bus device
- `0xBF` - reserved, to be in-sync with 0xFF
- `0xC0` - reserved, unused
- `0xC1…0xFE` - Parked left Loxone Tree bus device
- `0xFF` - broadcast to all devices

### Loxone Link to Tree Bus

The Tree Base Extensions forwards all broadcast messages to both branches and all direct messages to devices, which are known to be in either one of the branches. Only modifying the top 5 bits of the object identifier back from `0x11` to `0x10`.

A special case are parked devices (bit 7 in the device NAT set), in this case the message are sent to both branches. This also includes the special case of broadcasting (device NAT == 0xFF). The exception is a `NAT offer confirm`, which is always sent to the correct branch.

### Tree Bus to Loxone Link

All messages from the branches are always forwarded to the Loxone Link bus, the only change is in the top of the object identifier. The only special cases are a [Tree Shortcut Detection][tsd] and the `NAT offer confirm`, which set bit 6 in `B0`, if the message arrived via the Left Branch. After the NAT offer, this is no longer necessary, because the Miniserver will make sure to assign a NAT for the correct branch.

### Tree Shortcut Detection [tsd]

The Miniserver can detect if two Tree branches behind Tree Base Extensions are accidentally connected together. This can happen either by connecting the Left and Right Tree Bus or by connecting two Tree branches behind different Tree Base Extensions.

If a Tree Base Extension detects a server package on the Tree Bus by looking at the `dd` bits in the CAN object identifier, it will delete the lower bit in the `dd` bitmask and replace the package with a `Tree Shortcut` command and a device NAT of `0x00`. `B0` will contain a flag of `0x00/0x40` depending on Tree branch. This way the command will at least only executed once and the `Tree Shortcut` message arriving at the server can trigger an error.

The server will then start sending `Tree Shortcut Test` messages to the reserved device NAT 0x3F/0x7F for testing if the shortcut has been resolved. This messages is always forwarded by the Tree Base Extension and not replaced as mentioned above. This package contains the sending extension serial number in `val32` and the sending Tree branch in `B0`.


## Reason [reason]

Several commands contain a reason value telling why the command was send. Bit 5 defines a reset of a device. They are only used by the Miniserver to detect error conditions in extensions/devices.

| Reason  | Name    | Description |
| ------- | -------- | ----------- |
|  `0x00` | Undefined | Sent sometimes, if there is no reason. Probably a bug in some devices. |
|  `0x01` | Miniserver start |  |
|  `0x02` | Pairing | Sent by an extension in 'Start Info' in the startup phase, after the Miniserver was rebooted |
|  `0x03` | Alive requested | Sent by the Miniserver every 15 minutes to check the connection of extensions/devices |
|  `0x04` | Reconnect |  |
|  `0x05` | Alive package | Send by the extension/device in response to the `Alive` command or when sending an `Alive` packet at a regular interval. |
|  `0x06` | Reconnect (broadcast) |  |
|  `0x20` | Power on reset | Sent by extensions after a power failure. |
|  `0x21` | Standby reset | Device was in standby mode |
|  `0x22` | Watchdog reset | Watchdog task triggered a reset |
|  `0x23` | Software reset | Software reset triggered |
|  `0x24` | Pin reset | Reset via triggered via the NRST pin |
|  `0x25` | Window watchdog reset | a time based watchdog triggered, not used? |
|  `0x26` | Low power reset | Wakeup from low power mode |


## Device Type [dt]

The 4-bit devices type from legacy devices was replaced by 16-bit value in NAT extensions/devices. Loxone Link bus devices have bit 15 cleared, while Tree devices have bit 15 set.

| Device Type | Extension |
| --------- | -------- |
|  `0x01`   | Air Base Extension V2 (unreleased?) |
|  `0x04`   | DMX Extension V2 (unreleased?) |
|  `0x05`   | 1-Wire Extension V2 (unreleased?) |
|  `0x06`   | RS232 Extension V2 (unreleased?) |
|  `0x07`   | RS485 Extension V2 (unreleased?) |
|  `0x09`   | Modbus Extension V2 (unreleased?) |
|  `0x0A`   | RGBW 24V Dimmer V2 (unreleased?) |
|  `0x0B`   | Relay Extension V2 (unreleased?) |
|  `0x0F`   | Fröling Extension V2 (unreleased?) |
|  `0x11`   | reserved for the Tree Bus |
|  `0x12`   | Internorm Extension |
|  `0x13`   | Tree Base Extension |
|  `0x14`   | DI Extension |
|  `0x15`   | KNX Extension (unreleased) |
|  `0x16`   | AI Extension |
|  `0x17`   | AO Extension |
|  `0x8001` | Valve Actuator Tree |
|  `0x8002` | Motion Sensor Tree |
|  `0x8003` | Touch Tree |
|  `0x8004` | Universal Tree (unreleased) |
|  `0x8005` | Touch Pure Tree |
|  `0x8006` | LED Ceiling Light Tree |
|  `0x8007` | LED Surface Mount Spot RGBW Tree |
|  `0x8008` | LED Spot RGBW Tree Gen 1 |
|  `0x8009` | NFC Code Touch Tree |
|  `0x800a` | Weather Station Tree |
|  `0x800b` | Nano DI Tree |
|  `0x800c` | RGBW 24V Dimmer Tree |
|  `0x800d` | Touch Surface Tree |
|  `0x800e` | LED Surface Mount Spot WW Tree |
|  `0x800f` | LED Spot WW Tree Gen 1 |
|  `0x8010` | Room Comfort Sensor Tree |
|  `0x8011` | LED Pendulum Slim RGBW Tree |
|  `0x8012` | Alarm Siren Tree |
|  `0x8013` | Damper Tree |
|  `0x8014` | Leaf Tree |
|  `0x8015` | Integrated Window Contact Tree (unreleased) |
|  `0x8016` | LED Spot RGBW Tree |
|  `0x8017` | LED Spot WW Tree |
|  `0x8018` | Power Tree (unreleased) |
|  `0x8019` | Nano 2 Relay Tree |
|  `0x801a` | Ahri Tree (unreleased) |
|  `0x801b` | Magnus Tree (unreleased) |
|  `0x801c` | NFC Code Touch Tree (unreleased) |


## NAT Commands

Because there are 7 available data bytes, I use `B0`,`B1`,`B2`,`B3`,`B4`,`B5`,`B6` to identify them individually.

Some common values I have given a name:
`val16` = `B1-B2` is a 16 bit value in the little endian format: `(B1 + (B2 << 8))`
`val32` = `B3-B6` is a 32 bit value in the little endian format: `(B3 + (B4 << 8) + (B5 << 16) + (B6 << 24))`

Every numbers larger than 8 bit are always in the little endian format. Often a 32 bit value is used, even if only a few bits are important. In this case the other bits can be ignored and should be 0.

Commands fall into 3 groups:

- `0x00…0x7F`: typically common commands shared by all devices
- `0x80…0xEF`: send to/from devices to update values.
    - `0x80…0x8F`: regular value updates
    - `0x90…0x9F`: encrypted value updates, e.g. used by the NFC Code Touch
- `0xF0…0xFF`: device detection, NAT translation and handling of fragmented packages

| Command | Name    | Dir | Description |
| ------- | -------- | --- | ----------- |
|  `0x01`   | Version Request | S→E | Requests a Version Info package to identify an extension/device |
|  `0x02`   | Start Info | S←E | 20 bytes fragmented package: `B0…B3`: firmware version of device, `B4…B7`: unknown (0), `B8…B11`: configuration CRC, `B12…B15`:serial number, `B16`: [reason][reason], `B17…B18`:hardware type, `B19`:hardware version |
|  `0x03`   | Version Info | S←E | Identical to "Start Info" |
|  `0x04`   | Config Equal | S↔E | From server or extension/device after an "Alive" message or a "Start Info" to confirm that the configuration has not changed. |
|  `0x05`   | Ping | S→E | Requests a "Pong" reply |
|  `0x06`   | Pong | S←E | Reply to a "Ping" message |
|  `0x07`   | Set Offline | ? | Set extension/device offline |
|  `0x08`   | Alive | S→E | Every 15 minutes from the Miniserver to check if the extension/device is still active. `val16` contains the version of the configuration, val32 the STM32 CRC. `B0` the [reason][reason] for the request. |
|  `0x0C`   | Timesync | S→E | Heartbeat sync package with time. `(B0/B1 & 0x7fff)` is the current year. `(((B2 & 7)<<1) + (B1 >> 7))` is the current month. `(B2 >> 3)` the current day. val32 the ms since midnight. Devices use it to synchronize their LED blinking. |
|  `0x10`   | Identify | S→E | Broadcast by Miniserver, if inside the Loxone Config software an extension/device is selected. The LED will flicker very quickly to help identify it. The serial number is in val32 (deselected the device if the serial number doesn't match). `val16` is a timeout in seconds, I don't think it is actually used. |
|  `0x11`   | Send Config | S→E | Fragmented package, specific configuration for an extension/device |
|  `0x12`   | Webservice Request | S↔E | `B0`:0x00, `B1`:number of bytes starting `B2`, `B2…`: ASCII-string, zero terminated. Up to ~131 characters per packet. Several packets in a row a possible. Can be used to send commands _to_ a extension/device. |
|  `0x13`   | Logging | S←E | A string, like in "Webservice Request", used for error messages from an extension/device |
|  `0x15`   | Internorm Monitor | ? | ? |
|  `0x16`   | CAN Diagnostics Reply | S←E | Reply from an extension/device with CAN diagnostics |
|  `0x17`   | CAN Diagnostics Request | S→E | Request CAN diagnostics, used by Loxone Config |
|  `0x18`   | CAN Error Reply | S←E | Reply from an extension/device with CAN diagnostics |
|  `0x19`   | CAN Error Request | S→E | Request CAN Errors, used by Loxone Config |
|  `0x1a`   | Tree Shortcut | S←E | Used by the Tree Extension, if a server based package is received on the Tree Bus. This should never happen. |
|  `0x1b`   | Tree Shortcut Test | S→E | Used by the Tree Extension. Sent by the Miniserver to test if a reported shortcut on the Tree Bus still exists. |
|  `0x1c`   | KNX Send Telegram | ? | Used by an unknown KNX extension |
|  `0x1d`   | KNX Group Address Config | ? | Used by an unknown KNX extension |
|  `0x1e`   | Group Identify | ? | 16-bit:array element count, 16-bit: flag, 32-bit: ???, 6-byte array:[32-bit:serial, 8-bit:index , 8-bit:filler] |
|  `0x1f`   | Tree Link Sniffer Packer | ? | ? |


| Command | Phase    | Dir | Description |
| ------- | -------- | --- | ----------- |
|  `0x80` | Digital Value | S↔E | Set/Get digital value #`B0` in `val32` |
|  `0x81` | Analog Value | S↔E | Set/Get analog value #`B0`, full description below this table. |
|  `0x82` | Internorm Digital Value | ? | Set/Get an Internorm digital value |
|  `0x83` | Internorm Analog Value | ? | Set/Get an Internorm analog value |
|  `0x84` | RGBW Value | S→E | Set a RGBW value with red:`B3`,green:`B4`,blue:`B5` and white:`B6` |
|  `0x85` | Frequency Value | S↔E | Set/Get frequency value #`B0` in `val32` in Hz |
|  `0x86` | Keypad Code Input 1 | ? | ? |
|  `0x87` | Keypad Code Input 2 | ? | ? |
|  `0x88` | composite RGBW Value | S→E | Set a composite RGBW value with red:`B3`,green:`B4`,blue:`B5` and white:`B6` and a fading time of `val16` |
|  `0x89` | Keypad Value | S←E | Entered value on a Keypad |
|  `0x8a` | composite white Value | S→E | 15 byte fragmented package. Set a composite white value with value1:`B3`,value2:`B4`,value3:`B5`,value4:`B6`, fading time 1:`B7+(B8<<8)`, fading time 2:`B9+(B10<<8)`, fading time 3:`B11+(B12<<8)`, fading time 4:`B13+(B14<<8)`  |
|  `0x8d` | Tree Internorm Data Packet | ? | ? |
|  `0x90` | Crypt Digital Value | | After decryption, treated like "Digital Value" – only used by NFC Keypad |
|  `0x91` | Crypt Analog Value | | After decryption, treated like "Analog Value" – only used by NFC Keypad |
|  `0x92` | Crypt Code Value | ? | Digits entered on NFC Keypad |
|  `0x93` | Crypt NFC Value | ? | NFC ID recognozed on NFC Keypad |
|  `0x94` | Crypt Key Value | ? | Used to encrypt send/receive values – only used by NFC Keypad |
|  `0x98` | Crypt Device ID Reply | S←E | Reply from the Tree device to the Miniserver with the UID |
|  `0x99` | Crypt Device ID Request | S→E | For Tree devices the Miniserver requests the 12-byte STM32 UID |
|  `0x9a` | Crypt Challenge Rolling Key Reply | ? | Used to encrypt send/receive values – only used by NFC Keypad |
|  `0x9b` | Crypt Challenge Rolling Key Request | ? | Used to encrypt send/receive values – only used by NFC Keypad |
|  `0x9c` | Crypt Challenge Authorization Request | S→E | Miniserver sends challenge to extension |
|  `0x9d` | Crypt Challenge Authorization Reply | S↔E | Extension sends reply back to the Miniserver |
|  `0xef` | Firmware Update (new) | S→E | New firmware update format, it sends blocks as fragmented data |

The analog value is quite complex. `val32` is the value, but the flags in `val16` define how the value is interpreted:

Bit 0…3 in the flags are a scaling factor:

  - 0 = `* 1.0`
  - 1 = `* 1000.0`
  - 2 = `* 1000000.0`
  - 3 = `* 1000000000.0`
  - 4 = unused
  - 5 = `/ 1000.0`
  - 6 = `/ 1000000.0`
  - 7 = `/ 1000000000.0`
  - 8 = `/ 10.0`
  - 9 = unused
  - 10 = unused
  - 11 = unused
  - 12 = unused
  - 13 = unused
  - 14 = unused
  - 15 = unused
Bit 4: if set, the value is a signed value, otherwise it is unsigned.
Bit 6: unused
Bit 7: unused


| Command | Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | -------- | --- | -- | ----- | ----- | ----------- |
|  `0xf0` | Fragmented Package Header | S↔E | command | size | STM32 CRC | Header of a fragmented package |
|  `0xf1` | Fragmented Package Data | S↔E |  |  |  | 7 bytes of data of a fragmented package |
|  `0xf3` | Firmware Update | S↔E |  |  |  | Part of the firmware update |
|  `0xf4` | Identify unknown extension | S→E |  |  |  | Identify all extensions/devices, which don't have a valid NAT |
|  `0xf5` | KNX Monitor | S→E |  |  | KNX monitor state (0/1) | Only used by an unknown KNX extension. |
|  `0xfb` | Search devices Request | S→E |  |  |  | Search for extensions and devices |
|  `0xfc` | Search devices Response | S←E |  | hardware type | serialnumber | Responses from extensions and devices |
|  `0xfd` | NAT offer confirm | S→E | NAT | parked | serialnumber | The Miniserver confirms a NAT to an extension/device |
|  `0xfe` | NAT offer request | S←E |  | hardware type | serialnumber | An extension/device is requesting a NAT |

## Webservice Requests

Webservice Requests are a way to communicate with the device/extension. They are always ASCII strings and the reply is again an ASCII string. These requests are currently used by Loxone Config:

| WebService Request | Description |
| ------------------ | ----------- |
|         TechReport | Returns 'UpTime:%ds;Serial:%08x;NatIdx:%d;' |
|         Statistics | Returns the Loxone Link CAN Bus Statistic, like 'Sent:%d;Rcv:%d;Err:%d;REC:%d;TEC:%d;HWE:%d;TQ:%d;mTQ:%d;QOvf:%d;RQ:%d;mRQ:%d;' |

In the TechReport the fields are as follows:

|    Field | Description |
| -------- | ----------- |
|  UpTime  | Time in seconds since the last reboot or power-on of the device |
|   Serial | 8 character serial number of the device |
|   NatIdx | Active NAT Index of the extension/device |

In the Statistics the fields are as follows:

| Field | Description |
| ----- | ----------- |
|  Sent | Overall number of transmitted messages |
|   Rcv | Overall number of received messages |
|   Err | Number of CAN errors reported, also returned via CAN Error command |
|   REC | Current Receive Error Counter, also returned via CAN Error command |
|   TEC | Current Transmit Error Counter, also returned via CAN Error command |
|   HWE | Number of CAN error passive interrupts |
|    TQ | current number of elements in the transmission queue |
|   mTQ | maximum number of elements in the transmission queue |
|  QOvf | Queue overflow, if messages could not be send on time |
|    RQ | current number of elements in the receiving queue |
|   mRQ | maximum number of elements in the receiving queue |



## Communication Phase

There are three specific phases for the communication:
- Starting the Miniserver - during this phase the Miniserver identifies and configures all extensions and devices on the bus based on the Loxone configuration file.
- Running - messages send in a regular interval by the Miniserver and/or the extensions on the bus. Used to check if everything is fine, as well for synchronization.
- Software Update - special phase to update extensions and devices.

Besides these phases extensions and devices can report status changes at any time, like a switch being pressed, temperature changes, etc. In the same way can the Miniserver send device specific commands to devices, like turning a light on, etc. All these commands are device specific, while the communication phases are almost identical between all devices.


### During Miniserver Start

#### Miniserver
1. Miniserver sends multicast "Extensions offline" to the bus twice with a 50ms delay between them. It tells all extensions to not send data onto the bus during the start phase.
2. The Miniserver loads the Loxone Config file and tries to contact every extension in the config file in order. It  sends a broadcast command "NAT offer confirm" to which extension reply with a "Start Info" command. The Tree extension also replies with two CAN Error Replies (for both Tree branches) and a "configuration equal" response.
3. After iterating over all extensions, the Miniserver will then multicast to "Identify unknown extension". An extension or device will reply with a "NAT offer request" – with a random NAT. To which the Miniserver replies with a "NAT offer confirm" with a new NAT, which has bit 7 set (to park the extension). The extension/device will reply with the "Start Info" command.
4. For each Tree extension the Miniserver will now configure the devices behind it and search for unknown devices. This happens in the same way as it searched for Extensions:
    1. Send a "NAT offer confirm" to all known devices with the Tree extension NAT and a new device NAT. The device will reply with a "Start Info" command.
    2. Then send a "Identify unknown extension" multicast with the Tree extension NAT and a device multicast NAT of `0xFF`. This will trigger all devices to reply with a "NAT offer request" (the device ID is `0x00`) to which the server confirms with a "NAT offer confirm" and a final "Start Info" from the device. Unknown devices will always be parked (NAT has bit 7 set)

##### Authorization of Extensions and Tree devices

Starting with the latest 10.3 version of the Miniserver, the Miniserver now requires all Extensions and Tree devices to be authorized.

This is done to avoid hobbyists to make their own hardware. Why only hobbyists? Well, as a professional product pirate you would simply clone the hardware design and also copy the original firmware – then the Miniserver will see no difference between original Loxone hardware and copies and even happily install new firmware updates on the cloned hardware. Honestly: I think Loxone should simply _allow_ others to make devices and simply _charge_ professionals a potentially expensive license, like any other company in the world do. Locking out fans is generally not a good idea. End of my rant…

Ok, now lets explain the mechanism, it's a bit convoluted but not complex.

Authorization packages are 16 or 32 byte fragmented packages. They are encrypted with AES-128 CBC. The key and IV generated by the serial number of the device.

The Miniserver sends a Challenge Request package, which is decrypted with the serial number of the extension or device. It is then validated to verify the encryption succeeded. If the package was valid, the extension or device generates an AES key/iv pair from the serial number, a 12-byte device ID (which is constant for all extension, but Tree devices, for which it is the STM32 UID) and a random number, which was in the Challenge Request package. The AES key/iv pair is then used to encrypt a Challenge Reply package, which also has a header, a new random value and 8 filler bytes, which are ignored by the Miniserver. The Miniserver also solves the challenge (all 3 required values are known to the Miniserver) to try to decrypt the Challenge Reply package with the calculated AES key/iv values. If it didn't succeed, it retries – I think – more 6 times, before the extension or device is put offline with the error message "Authorization failed".

Tree devices have one more layer, probably inherited from the NFC Keypad, which had this before all other Tree devices. For these devices the challenge needs to know the 12-byte device ID. It is request before the challenge via a Device ID Request. The decryption of the request is using a different AES key/iv master compared to the Challenge Request, but is otherwise the same. The device always replies with a 32-byte Device ID Reply package after receiving this request, but if the request was invalid, it will reply an encrypted package with an invalid header and no device ID. If the reply was valid, the device ID is stored with the serial number of the device inside the `/sys/device/settings.bin` file and _never_ requested again. That said: you can just delete this file via any FTP client directly on the Miniserver and reboot. It will automatically be recreated after the Miniserver requested new device IDs. This device ID is then used in the challenge instead of the constant one, which is used for all legacy extensions and NAT based extensions. Only Tree devices support the device ID. I am not sure _why_, because at least for NAT based extensions it is even a special case to not do this.

There is a 3rd encryption/decryption way, which is used to encrypt packages with values. This is currently only used for the NFC Keypad. The algorithm is almost the same, but uses different AES key/iv and sending and receiving these data packages. It also uses a rolling key mechanism, so after every package send/received the iv changes – every 10s or at init it re-syncs, so that a lost package does not break the transfer forever. I am not gonna document this here, because the need for your own NFC Keypad is probably minor.

Ok, next step with more technical details:

All packages start with a two 32-bit values as the header. The first 32-bit value is always `0xDEADBEEF`, which acts as a check if the package was decrypted correctly. The next 32-bit value is a random value, which is randomizing the encrypted packages, but also used as a parameter for the challenge during the Authoization phase. 8 more bytes are following, typically they contain no information and are used as padding to create 16-byte packages (needed for the AES-128). The Device ID Reply package is 32-byte large, because the device ID is 12-byte large.

For encryption/decryption we need 5 constants, which are stored in the code of the Miniserver and all extensions – I reference them by name.
- `CryptoCanAlgoKey` - 16-byte AES key
- `CryptoCanAlgoIV` - 16-byte AES IV
- `CryptoCanAlgoLegacyKey` - 16-byte AES key
- `CryptoCanAlgoLegacyIV` - 16-byte AES IV
- `CryptoMasterDeviceID` - 12-byte device ID / STM32 UID, used for all extensions, but not Tree devices.

`CryptoCanAlgo_DecryptInitPacket` is used to decrypt the Authorization Request. It is not using the CryptoCanAlgoKey/CryptoCanAlgoIV directly, but modifies it with the 32-bit serial number of the device. The AES key is split into 32-bit words, which are XORed with the inverted serial number. The AES iv is split into 32-bit words, which are XORed with the serial number. Then the 16-byte block is decrypted with a standard AES-128 CBC. `CryptoCanAlgo_EncryptInitPacket` is the above one for encryption – only needed by the Miniserver.

`CryptoCanAlgo_DecryptInitPacketLegacy` and `CryptoCanAlgo_EncryptInitPacketLegacy` is identical to the above functions, it just uses the legacy AES key/iv. It is used for device ID requests/replies and to send rolling key updates.

`CryptoCanAlgo_DecryptDataPacket` and `CryptoCanAlgo_EncryptDataPacket` are used to decrypt the Challenge Reply and rolling key based value encryption. The do not use the serial number, but the AES key/iv pair generated key by the solver of the challenge. The iv from the solver is just a 32-bit value, while the key is a 128-bit value. The four 32-bit words of the key are XORed by the iv value and the AES IV, which has to be 128-bit is simply the 32-bit IV value four times.

`CryptoCanAlgo_SolveChallenge` is solving a challenge presented by the Miniserver. It takes a 32-bit random value, send by the Miniserver in the Challenge Request package, the device serial number and the 12-bit device ID. These values are combined into a 20-byte block: 12-byte device ID, the 32-bit random number and the 32-bit serial number. The 128-bit AES key consists out of four 32-bit values:

    aesKey[0] = RSHash(20-byte block)
    aesKey[1] = JSHash(20-byte block)
    aesKey[2] = DJBHash(20-byte block)
    aesKey[3] = DEKHash(20-byte block)
    aesIV = RSHash(20-byte block with every byte being XORed with 0xA5 before)

A lot of different hash functions, picked from a popular hash list…

RSHash = Robert Sedgwick's "Algorithms in C" hash function.
JSHash = A bitwise hash function written by Justin Sobel. Ignores the seed when 0.
DJBHash = An algorithm produced by Professor Daniel J. Bernstein and shown first to the world on the usenet newsgroup comp.lang.c. It is one of the most efficient hash functions ever published. Substitutes the algorithm's initial value when the seed is non-zero.
DEKHash = An algorithm proposed by Donald E. Knuth in "The Art Of Computer Programming, Volume 3", under the topic of sorting and search chapter 6.4. Substitutes the algorithm's initial value when the seed is non-zero.

This is all that is needed. The encryption is quite insecure, because for non-tree devices you can simply decrypt packages picked of the CAN bus. The only variance is a 32-bit value (the serial number), which can be brute forced (or found out during a reboot of the Miniserver). The random number range is typically also only a low value and can be brute forced, if necessary. The device ID can be requested at any time from a device, not need to hack it. Is there a better solution? No, if the system should also be tolerant to lost packages every now and then. It feels overkill, increases the bus load significantly, can trigger errors and only solves a problem that doesn't exist for Loxone (protecting against commercial product piracy) without actually protecting against them.


#### Extension and Device

An extension or device on power-on immediately starts sending a "Start" command every second to inform the Miniserver about its existence.

The "Extensions offline" or "Park unused extension" from the Miniserver will stop this repeated sending of a message. After that the extension just follows the commands issued by the Miniserver during start. This repeated "Start" command is allowing the Miniserver to detect a reboot of an extension and the need to start it properly, e.g. by configuring it. A common scenario is the firmware update of an extension, but you could also power on an extension after the Miniserver – something Loxone specifically does _not_ recommend.


### Running/Idle

About once per minute the Miniserver sends "Timesync" with the current date and time in ms since midnight. All NAT extensions and devices are using it to detect a working bus and to synchronize their LED blinking.

Every 10 minutes the Miniserver sends an "Alive" message to the extension/device. It will verify the CRC and either send a "Config Equal" or an "Alive" message with the current config CRC. Because the CRC from the server is typically `0x00000000`, the response will allmost never be "Config Equal". The Miniserver expects the response within 3s – otherwise the Miniserver will assume the device is offline. If the extension/device responds with a different CRC, the Miniserver will send updated configuration.

There is a second way for an extension to detect that the bus is not working, by simply counting the communication errors of the CAN bus. If there are too many, the extension will also switch to an error state.


### Firmware update

The firmware update process for NAT extensions and devices is quite different from legacy devices. The Miniserver checks the version number as reported of extensions and devices. If the version number is below the current number, the Miniserver will try to install an update. All packages are fragmented packages of the 0xf3 command. The fragmented package contains a subcommand for the update-process-only.

| Offset  | Size    | Description |
| ------- | ------- | ----------- |
|       0 | 1 byte  | Size of the fragmented package |
|       1 | 1 byte  | Subcommand  |
|       2 | 2 bytes | [Device type][dt] |
|       4 | 4 bytes | New firmware version number |
|       8 | 2 bytes | Page |
|      10 | 2 bytes | Index |
|     12… | 0+ bytes | Up to 64-bytes of optional data |

| Subcommand | Send type | Description |
| ---------- | --------- | ----------- |
|          1 | Broadcast | Firmware data for address = `Page * 0x800 + Index * 0x40`, the package contains 64 bytes of data |
|          2 | Broadcast | CRC data over all pages, each page has a 32-bit STM CRC. Starts at `Page` from the header above. |
|          3 | Direct    | Verify the update by comparing the CRC over all pages (`Page` from the header is the number of pages) |
|          4 | Direct    | Verify the update and reboot the extension/device (no message is sent to the server) |
|       0x80 | from Device | Confirm success of the verify, `Page` is 0 and the actual 32-bit CRC in the optional data area |
|       0x81 | from Device | Confirm failure of the verify with the defect page in `Page` and the actual 32-bit CRC in the optional data area |

The process happens in 3 phases:

1. The complete new firmware is send via broadcast messages to all extension/devices. The extension/device will accept it, if it's version number of the update is newer than the current one and the [device type][dt] matches. The firmware is then stored in a special update area of the flash.
2. After the whole transfer, the CRCs over all pages are transferred, also via broadcast.
3. Finally the Miniserver will send a verify command to each extension/device individually. The extension/device will verify the update and reply to the server with a success or failure message. If this message doesn't arrive, the Miniserver will retry the verify ~20 times before starting the whole update process again. After 5 unsuccessful updates, the Miniserver gives up till the next restart.

To avoid further updates, an extension/device could just take the new version from the update page and confirm the update. As long as the protocol is not extended or changed by Loxone, it should just work.


## Configurations in devices

A configuration for a device is stored in flash memory after uploaded by the Miniserver. The Miniserver checks the STM32 CRC and the version number of the configuration and re-uploads them, if necessary. For the calculation the size of the configuration is rounded up to the next 4 bytes and then the last 4 bytes are ignored from the calculation and are always 0x00000000.

Configurations in devices all seem to share a similar header. When describing devices you can assume that the first 8 bytes are the same.

| Offset  | Description |
| ------  | ----------- |
| 0       | Size of the configuration in bytes |
| 1       | Version of the configuration. Can be changed by a firmware update. |
| 2       | Blink synchronization offset of the LED, can be 0xFF, if the device doesn't have a normally visible LED, e.g. the Touch devices |
| 3       | unused, 0x00 |
| 4..7    | Time in seconds after the last message from the Miniserver, the Miniserver is considered offline. 10% before reaching this limit, an Alive packet is sent out, which should trigger a reply. That said: the time sync messages every minute will extent the timeout, so every value above 60s seems overkill. The default is 900s. |


## Device specific commands

- [Loxone DI Extension](LoxoneLinkNATExtensionDI.md)
- [Loxone AI Extension](LoxoneLinkNATExtensionAI.md)
- [Loxone AO Extension](LoxoneLinkNATExtensionAO.md)
- [Loxone Tree Extension](LoxoneLinkNATTreeExtension.md)
- [Loxone Touch Tree Device](LoxoneLinkNATTreeTouch.md)
- [Loxone Touch Pure Tree Device](LoxoneLinkNATTreeTouchPure.md)
- [Loxone Valve Acutator Tree Device](LoxoneLinkNATTreeValveActuator.md)
- [Loxone Damper Tree Device](LoxoneLinkNATTreeDamper.md)
- [Loxone LED Devices](LoxoneLinkNATLED.md)
- [Loxone RGBW 24V Dimmer](LoxoneLinkNATTreeRGBW24VDimmer.md)
- [Loxone Room Comfort Sensor](LoxoneLinkNATTreeRoomComfortSensor.md)
- [Loxone Alarm Siren](LoxoneLinkNATTreeAlarmSiren.md)
- [Loxone Leaf Tree](LoxoneLinkNATTreeLeaf.md)
- [Loxone Weather Station Tree](LoxoneLinkNATTreeWeatherStation.md)
- [Loxone Motion Sensor Tree](LoxoneLinkNATTreeMotionSensor.md)
- [Loxone LED Ceiling Light Tree](LoxoneLinkNATTreeLEDCeilingLight.md)
