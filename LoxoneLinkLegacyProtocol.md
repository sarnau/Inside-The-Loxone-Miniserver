# Loxone Link Legacy protocol

The CAN object identifier is 29 bits long and follows a simply scheme for the legacy extensions: the lower 24 bits are a unique serial number (not equal 0), as represented by the letter `a`, 4 bits are the device type `tttt` and bit 28 is the sending direction `d` (0 = sent _from_ the extension, 1=sent _to_ an extension):

    dtttt.aaaaaaaa.aaaaaaaa.aaaaaaaa

The command is the first byte in the 8 byte data package. The remaining 7 bytes are payload data, which depend on the command. Bit 7 in the command byte is set by extensions when sending a command, while the Miniserver sends commands with bit 7 cleared. That said, it seems the Miniserver and the Extensions filter it out and ignore its phase.

The following extensions are known to follow the legacy protocol:

| Type | Extension Name / Type |
| ---- | ---- |
|  0x0 | Broadcast (only used by the Miniserver) and the newer NAT protocol. |
|  0x1 | Extension |
|  0x2 | Dimmer Extension |
|  0x3 | EnOcean Extension |
|  0x4 | DMX Extension |
|  0x5 | 1-Wire Extension |
|  0x6 | RS232 Extension |
|  0x7 | RS485 Extension |
|  0x8 | IR Extension |
|  0x9 | Modbus 485 Extension (This is the shipping one) |
|  0xA | Fröling Extension (used by the Fröling Extension see below) |
|  0xB | Relay Extension |
|  0xC | Air Base Extension |
|  0xD | Dali Extension |
|  0xE | Modbus 232 Extension (Unknown extension) |
|  0xF | Fröling Extension as part of the serial number (Miniserver sends to `0xA` instead, probably because `0x1F` is already reserved for software updates...) |

The Miniserver does not have nor does it need a serial number on the CAN bus. It either sends broadcast messages or sends direct messages to extensions. It also listens to all messages on the bus.

The legacy protocol uses the object identifier in the following ways:

| Object Identifier | Description |
| ------- | ----------- |
| `0x00000000` | multicast to all legacy extensions. Used by the Miniserver to send commands to all extensions on the bus. |
| `0x00______` | unused, because the Miniserver does not have a serial number on the bus. |
| `0x1taaaaaa` | send a command to an extension with the serial number `taaaaaa` with 't' being the type from above. |
| `0x0taaaaaa` | send a command from an extension with the serial number `taaaaaa` with 't' being the type from above. |
| `0x10______` | this is reserved and used for the new NAT protocol (see in its own chapter) |
| `0x0F______` | unused, because it conflicts with the firmware update (see above) |
| `0x1Fttpppp` | used by the Miniserver to send 8 bytes of updated firmware to all extensions of type `tt` to the package position `pppp`. More information in the update chapter. |

An extension with the serial number `taaaaaa` of type `tt` (only types from 0x00…0x0F are used, because `0x10` represents the sending direction) uses CAN filters to only listen to commands on the bus, which are of relevance to it. These CAN filters allow the extension to ignore every messages, which is of no use for it therefore reducing its CPU load.

| Filter       | Mask         | Description |
| ------------ | ------------ | ------- |
| `0x00000000` | `0x1FFFFFFF` | multicast to all extensions |
| `0x0t000000` | `0x1FFFFFFF` | multicast to all extensions of this type - only used in the software update case. |
| `0x1taaaaaa` | `0x1FFFFFFF` | data send to the extension directly |
| `0x0taaaaaa` | `0x1FFFFFFF` | data send from the extension, technically that is unimportant, because only the extension itself will send this package. The extension can use it to check if a package was actually send out. |
| `0x1Ftt0000` | `0x1FFF0000` | listen to update data for the type of extension, the lower 16 bits contain the package number and are ignored by the filter |


## Legacy Commands

Because there are 7 data bytes, I use `B0`,`B1`,`B2`,`B3`,`B4`,`B5`,`B6` to identify them individually.

Some common values I have given a name:
`val16` = `B1-B2` is a 16 bit value in the little endian format: `(B1 + (B2 << 8))`
`val32` = `B3-B6` is a 32 bit value in the little endian format: `(B3 + (B4 << 8) + (B5 << 16) + (B6 << 24))`

Every numbers larger than 8 bit are always in the little endian format. Often a 32 bit value is used, even if only a few bits are important. In this case the other bits can be ignored and probably should be 0. If no parameters are mentioned, then the content of the package is irrelevant and often contains random garbage.

Please remember that commands _from_ extensions always have bit 7 in the command byte set, while the server sends commands with bit 7 cleared. There is no technical reason for it, because the object identifier already contains the direction, but it is done that way anyway.

| Command | Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | -------- | --- | -- | ----- | ----- | ----------- |
|  0x00   | Start    | S→E |    |       |       | Identify a known device |
|  0x01   | Update   | S→E | minimum hardware version required for this update | `0xDEAD` => force update, ignore the version | version of this update | Start a firmware update |
|  0x02   | Update   | S→E | 0x00 | `0xDEAD` => force reboot, ignore the version | version of the update | Reboot extension, if necessary |
|  0x03   | Update   | S→E | bit 0==1: enforce update, ignore version number, bit 1==1:verify modules update | number of 1kb pages | version of the update | Verify update |
|  0x04   | Start    | S←E | 0x00 | bitmask of configs | version number of extension | Acknowledge receival of the configuration |
|  0x05   | Update   | S←E | 0x00 | 0x0000 | version number of extension | ACK, Acknowledge the update request of a `0x01` command |
|  0x06   | Update   | S←E | 0x00 | 0x0000 | version number of extension | NAK, Not acknowledge the update request of a `0x01` command, cancel it. |
|  0x07   | Start    | S←E | hardware version of extension | version of FLASH configuration (0=none) | version number of extension | Start command, send after the bus connection was interrupted. |
|  0x08   | Loxone Config | S→E |    |       |       | Identity LED. Makes the LED on the extension flash really fast to identify it. Reset by sending this command as a multicasting command. |
|  0x09   | Idle     | S↔︎E | hardware version | version of FLASH configuration (0=none) | version number of extension | Alive request is send every 6 minutes _plus_ the low 6 bits of the extension serial number in seconds. This avoids that all extensions send this command at the exact same time onto the bus. Parameters are identical to the `0x07` command. The receiver replies with  a `0x0F` command to confirm the communication within 3s after sending this request, otherwise the communication is broken. Typically send _from_ the extension _to_ the Miniserver, but the other direction is possible as well. |
|  0x0A   | Update   | S→E | minimum hardware version required for this update | `0xDEAD` => force update, ignore the version | version of this update | Init update modules. Only implemented in the IR Extension, otherwise ignored. |
|  0x0B   | Start    | S→E |    |       |       | Identify unknown extension. |
|  0x0C   | Start    | S→E |    |       |       | Set an extension offline (multicast command as well). The extension will start blinking orange, but is not muted.  Identical implementation as `0x37`. |
|  0x0D   | Idle     | S→E |    |       | delta time since last heartbeat in ms  | Heartbeat sync send about once per minute, used to synchronize the blinking between all extensions. Can be used by extensions to detect an active CAN bus. |
|  0x0E   | Start    | S→E |    |       | blink position in 6.2ms units | Blink position. This is used to have all LEDs blink out-of-sync. This also triggers an extension to report its status back to the Miniserver after a reboot. |
|  0x0F   | Idle     | S↔︎E |    |       |       | Alive Reply to a `0x09` command to confirm the connection. |
|  0x1D   | Loxone Config | S↔︎E | flag |       | 32-bit value | Return diagnostics data, only implemented in a few extension. flag==2:more data to come, flag==3:data complete. |
|  0x2D   | Idle     | S→E | see right  | see right | time in ms since midnight | Heartbeat sync package with time. `(B0/B1 & 0x7fff)` is the current year. `(((B2 & 7)<<1) + (B1 >> 7))` is the current month. `(B2 >> 3)` the current day. Extensions seems to ignore that command. |
|  0x34   | Update   | S→E | see right | see right | 32 bit word | Write 32 bit word at 24 bit address (B0-B2). If the low-byte of an address is 0x00, the whole page will be erased first. Used if a CRC error was reported back to send certain bytes again. |
|  0x36   |          | S←E |    | settings version | settings CRC32 | Report current settings to the Miniserver. Send during boot, after being identified by the Miniserver. Forces the Miniserver to upload the configuration, if it detects a mismatch. |
|  0x37   | Start    | S→E |    |       |       | Park all devices (multicast command as well). Send to all extensions, which are known, but unused by the Miniserver configuration. Identical implementation as `0x0C`. |
|  0x38   | Loxone Config | S←E | 0x00 | B1:CAN Receiver Errors, B2:CAN Transmitter Errors | CAN error count | Reply package containing the CAN diagnostics. |
|  0x39   | Loxone Config | S→E |    |       |       | Request CAN diagnosis package - send continuously during 'Loxone Link Diagnostics' |
|  0x53   | Idle     | S←E |    |       | temperature | Overheating warning from an extension. More explanation below. |
|  0x54   | Update   | S→E | 0x00 | page number | CRC32 value | Send page CRC to verify update |
|  0x5B   | Update   | S→E |    |       |       | Mute an extension. The extension will no longer send any messages, not triggered by a specific request (alive messages, overload monitoring, CAN diagnostics) |
|  0x78   | Start    | S↔︎E | see right | see right | see right | Send a 7 byte checksum to the extension, if different: update the checksum and write settings to FLASH. An extension can send back zeros, if there is no valid configuration. |
|  0x79   | Start    | S→E | see right | see right | see right | Request the current configuration checksum. This allows the Miniserver to detect, if the configuration needs to be updated. If the extension doesn't respond this this, it will get a new configuration. |

Interestingly it is possible to send a `0x2D` command as an extension, the Miniserver will  detect it as a DCF77 package and set its internal clock. It seems that Loxone at some point had a DCF77 receiver planned or developed, but eventually decided that NTP is good enough. This command can only be send _once_ after a reboot of the Miniserver.

#### Overheating protection

Extensions with overheating protection (Extension, Relay Extension and Dimmer Extension) send the temperature following their `0x09` packages (every about 6 minutes) and after the `0x0e` package to provide the Miniserver with a reasonable update of the current temperature. If the temperature changed by about 5℃ – which is checked about every second – the overheat message will also be send. The temperature is measured internally with the build-in temperature sensor of the CPU.

The package format is a bit special: Older extension (hardware 0 or 1) always return the temperature data in its raw format. To get the temperature in ℃, you need to apply this formula: `℃ = (1475-(value32*2245/1024))/10`. Newer hardware can return the temperature in 0.1℃, if `B1` is set to a value different from `0x01`. `B2` contains the emergency shutdown flag (`!=0x00` when the device did shut down). The Extension and Relay Extension will shutdown when the internal temperature is above 87℃ for more than 3s, it will then turn off all relays to avoid further heat. After being in overheating mode, the extension will wait for the temperature to drop below 72.6℃, it then reboots to resume normal operation.


### Fragmented packages

To send more than 7 bytes of data for a command, the Miniserver sends fragmented packages. The are commonly used to transmit configurations or more complex commands. Two different ways to deal with fragmented packages are implemented in the Miniserver:

1. Command `0x44` with `B0` containing the block number. `B0 == 0` is the start block, which contains in `B1` the type of the block, `B3/B4` the number of bytes to be transferred and in `B5/B6` the unsigned 16 bit sum of all bytes in the data block. Blocks with `B0 > 0` contain 6 bytes of data each (except potentially the last one). With 255 possible blocks of 6 bytes each, it means that this command can transfer up to 1530 bytes. If the configuration settings block is larger, then option 2 is required and used by the Miniserver automatically.

2. Command `0x46` is send first by the Miniserver and it contains the header, identical to `0x44`. After the header block, the server then sends `0x45` blocks with 7 bytes of payload each (the last one block can contain less data, depending on the overall package size).

The fragments are buffered in the extension till all are transmitted and simply ignored silently if e.g. the checksum is wrong. The type of the block is very important for an extension to differentiate between different large packages, e.g. configuration data has a type of `0x06`.

## Communication Phase

There are three specific phases for the communication:
- Starting the Miniserver - during this phase the Miniserver identifies and configures all extensions and devices on the bus based on the Loxone configuration file.
- Running - messages send in a regular interval by the Miniserver and/or the extensions on the bus. Used to check if everything is fine, as well for synchronization.
- Software Update - special phase to update extensions and devices.

Besides these phases extensions and devices can report status changes at any time, like a switch being pressed, temperature changes, etc. In the same way can the Miniserver send device specific commands to devices, like turning a light on, etc. All these commands are device specific, while the communication phases are almost identical between all devices.


### During Miniserver Start

#### Miniserver
1. Miniserver sends multicast "Extensions offline" to the bus twice with a 50ms delay between them. This command is send in the legacy format and in the NAT format. It tells all extensions to not send data onto the bus during the start phase.
2. The Miniserver loads the Loxone Config file and tries to contact every extension in the config file in order. It first sends a command "Identify" to which extension reply with a "Start" command.
    1. If they have a persistent configuration, that package will also contain with the checksum over their configuration data to allow the Miniserver to check if an update of the configuration is needed.
    2. The Miniserver might also manually configure the extension based on its type.
    3. The extension might send back it's current values, e.g. inputs to make sure the server has the current values.
    4. At the end the Miniserver sets the LED blink position.
    5. Because setting the blink position in an extension is the last command by the Miniserver in the start phase to a specific extension, it can also trigger the extension to immediately report its status back to the Miniserver (inputs, sensor data) to allow the Minisever to have current values at the end of the start phase. Which status are reported back depends on the extension.
3. After iterating over all extensions, the Miniserver will then multicast to identify unknown extensions. The Miniserver sends this package twice: once for the legacy format and once for NAT. While they will not work unconfigured, it does allow the Loxone Config application to see them for further configuration.
4. Extensions which are known, but unused will then be send a "park unused extension". This will stop an extension from sending data to the bus and only listen to be configured at some point.
5. After extensions are configured, devices behind a Tree extension will be configured. Because they are always use the NAT protocol, I will document that in the NAT chapter.

#### Extension

An extension on power-on immediately starts sending a "Start" command every second to inform the Miniserver about its existence. The "Extensions offline" or "Park unused extension" from the Miniserver will stop this repeated sending of a message. After that the extension just follows the commands issued by the Miniserver during start. This repeated "Start" command is allowing the Miniserver to detect a reboot of an extension and the need to start it properly, e.g. by configuring it. A common scenario is the firmware update of an extension, but you could also power on an extension after the Miniserver – something Loxone specifically does _not_ recommend.


### Running

#### Miniserver
About once per minute the Miniserver sends several multicast messages:

- a legacy heartbeat "Send Sync Time" with the ms since the last heartbeat. This is used by extensions to detect if the Miniserver is online and that the bus is working. It is also used to synchronize the LED blinking pattern. The blink position is a value in 16ms steps to delay the blinking pattern of the green LED after a heartbeat sync was received. By using different numbers, the LEDs on all extension blink out-of-sync, but in a specific order
- the current date and time in ms since midnight. I have yet to find a legacy extension, which uses this message. The Miniserver sends this package twice: once for the legacy format and once for NAT. All NAT extensions and devices are using it to detect a working bus.

#### Extension
Wired extensions send an "Alive" command about every 6 minutes to the bus. The server replies to this message with an "Alive Reply". Extensions and the Miniserver are using these messages to test that all extensions and devices are working properly. While typically the Extension sends the "Alive" message, extensions also reply to an "Alive" command from the server with an "Alive Reply". If the receiver doesn't reply within 3s to this reply, the bus will be assumed offline and the LEDs are signaling an issue. An extension then starts to send a "Start" command every second to trigger the communication with the server again. The server either responds by setting up the extension or sets the extension offline, if it is not configured via Loxone Config.

There is a second way for an extension to detect that the bus is not working, by simply counting the communication errors of the CAN bus. If there are too many, the extension will also switch to an error state.


### Software Update

The software update process a special case, which is a bit more complex. Updates are always send to all extensions of the same type at the same time. An extension stores all data in a separate area of the flash memory and also receives the CRC32 checksums over all packages before applying the update.

The Miniserver receives the firmware version of the extensions during startup and also with an alive ping during idle. If there is a firmware update available, which will have a higher firmware version than the existing one, it will send the firmware to all extensions of the same type at the same time. Only after validation it is being copied into its final position with the booter code in the firmware.

To initiate the update, the Miniserver sends a multicast "Init Update" to the extensions. This package contains the new firmware version and the hardware revision, which the update is targeted for. If the hardware revision is too new, the update will be ignored by the extension, also if the firmware version is already identical (there is a way to force a reinstall by the server). If all is ready, the firmware update flash is erased and the extension awaits the firmware while blinking orange. It also replies with an ACK command to the server confirming the update. If the firmware version already matches, it will send back a NAK command.

It then sends via multicast the firmware to all extensions. The firmware is send in 8 byte packages and the lower word of the CAN object identifier contains the package number. A package number of `FFFF` finishes the upload.

Then the Miniserver – again via multicast – sends CRC32 packages for every 1024 byte page. These CRC32 are just buffered by the extension till a request to actually verify the data.

Then followed by a "Verify Update" multicast command. The extension will use the received CRC32 packages to verify all received package. If a CRC error occurred, it replies with the page number and the wrong CRC. This allows the Miniserver to retransmit this page. The Miniserver can also force a firmware verification, if necessary. This command is tried up to to 10 times.

The final step is a "Reboot" command, which will only execute if the firmware version actually changed (or if enforced by the server)


#### Emulation case for the update
If you try to emulate a device on the CAN bus, you might need to make sure to be at the current version, otherwise the Miniserver will try to update the firmware many times. If the update contains significant protocol changes, then there is nothing you can do, but if it is just a minor bugfix update, you can do the following:

- On "Init Update" reply NAK. The Miniserver seems to ignore it, but it feels like a good practice to tell the server that you don't want the update.
- On "Verify Update" store the provided version number. This is the new version number of the update.
- On "Reboot" check if your version number is different from the new version number. If so, update your version number to the new one and reboot.


## Device specific commands

- [Loxone Extension](LoxoneLinkLegacyExtension.md)
- [Loxone Relay Extension](LoxoneLinkLegacyExtensionRelay.md)
- [Loxone RS232 Extension](LoxoneLinkLegacyExtensionRS232.md)
- [Loxone RS485 Extension](LoxoneLinkLegacyExtensionRS485.md)
- [Loxone DMX Extension](LoxoneLinkLegacyExtensionDMX.md)
- [Loxone 1-Wire Extension](LoxoneLinkLegacyExtension1Wire.md)
- [Loxone Modbus Extension](LoxoneLinkLegacyExtensionModbus.md)
