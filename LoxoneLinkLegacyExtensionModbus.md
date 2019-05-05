# Modbus Extension (`0x09`)

This extension is from the hardware standpoint identical to the [RS485 extension](LoxoneLinkLegacyExtensionRS485.md), because Modbus is just an RS485 bus anyway. However it does encode and decode the Modbus protocol.

## Send write command to Modbus

The Modbus Extension only supports a limited number of write functions. Because of that, I have simply listed them all, which is much easier to read than trying to understand the Loxone documentation.

| Command | Modbus write function        | Modbus telegram    |
| ------- | ---------------------------- | ------------------ |
|  0x5D   | Single Coil                  | `B0` 0x05 `B1` `B2` `B3` `B4` CRC16-Modbus |
|  0x5E   | Single Register              | `B0` 0x06 `B1` `B2` `B3` `B4` CRC16-Modbus |
|  0x5F   | Multiple Registers           | `B0` 0x10 `B1` `B2` 0x00 0x01 `B3` `B4` CRC16-Modbus |
|  0x60   | Multiple Registers (2 regs)  | `B0` 0x10 `B1` `B2` 0x00 0x02 `B3` `B4` `B5` `B6` CRC16-Modbus |
|  0x61   | Single Register (4-bytes)    | `B0` 0x06 `B1` `B2` `B3` `B4` `B5` `B6` CRC16-Modbus |
|  0x62   | Multiple Registers (4-bytes) | `B0` 0x10 `B1` `B2` 0x00 0x01 `B3` `B4` `B5` `B6` CRC16-Modbus |

`B0` is the address of the device
`B1/B2` is the start register number. Loxone uses LSB for 16-bit, but Modbus MSB.
`B3-B6` are data values

## Reading registers

The Modbus extension calls the Modbus read function automatically and sends the values back to the Miniserver. It has to be configured for that. This is done by uploading the configuration via a fragmented package of type `0x06` (config). The configuration is 0x810 bytes large and always version 1.

| Offset |  Type  | Description |
| -----: | :----: | :---------- |
|      0 | 32-bit | 0xFEEDFEED = magic to detect that the package is valid |
|      4 | 16-bit | Version of the settings, always 1 |
|      6 |  8-bit | 0:automatic timing (based on the baudrate), !=0:manual timing flag (timing pause and timing timeout are used) |
|      7 |  8-bit | 0x00, unused filler |
|      8 | 32-bit | baudrate (2400,4800,9600 or 19200 are typical) |
|   0x0C |  8-bit | wordlength (5,6,7,8, Modbus requires 8) |
|   0x0D |  8-bit | parity (0=no parity, not in the Modbus specification, but very common) |
|   0x0E |  8-bit | one/two stop-bits (0=one stop-bit) |
|   0x0F |  8-bit | protocol == 3 (Modbus?) |
|   0x10 | 32-bit | timing pause, default: 10ms between packages |
|   0x14 | 32-bit | timing timeout, default: 1000ms for a response |
|   0x18 | 32-bit | number of entries in the following table |
|   0x1C | 8 byte packages | entries for read function requests |
|  0x80C | 32-bit | 0x000000, zero filler |

Description of a single 8-byte entry:

| Offset | Description |
| -----: | :---------- |
|      0 | 1…255: Address of the Modbus device (0 would be broadcast) |
|      1 | Modbus function code |
|      2 | 16-bit register number |
|      4 | 32-bit polling cycle and flags |

The 32-bit value is a bit complex:

| Bit(s) | Description |
| -----: | :---------- |
|   0…11 | polling cycle |
|     12 | 0:100ms, 1:1000ms; factor for the polling cycle to have the delay in ms |
|     13 | 1:combine 2 registers for a 32-bit value |
|     14 | register order (0:low/high, 1:high/low) |
|     15 | byte order (0:MSB, 1:LSB) |

The Modbus extension enforces a minimal 5s polling interval. A custom Modbus extension may not enforce it.

With the configuration uploaded and the extension not muted, the Modbus extension will send all polling requests based on the timing, but only one per 2ms. The send request is created from the entry table as follows:

For read coils (1) and read discrete inputs (2):

    `address` `function code` `MSB register number` `LSB register number` 0x00 0x01 CRC16-Modbus
    
For read holding registers (3) and read input register (4):

    `address` `function code` `MSB register number` `LSB register number` 0x00 0x01/0x02 CRC16-Modbus

The 0x01/0x02 is depended if bit 13 (combine 2 registers) is set or not.

For any other function code:

    `address` `function code` `MSB register number` `LSB register number` CRC16-Modbus

The reply is parsed (based on the function code and the bits in the polling cycle flags) and send back to the Miniserver. If an error occurs, an error command is reported back:

| Command |             B0 | B1/B2 |      B2/B3      |     B4/B6    | Description |
| ------- | -------------- | ----- | --------------- | ------------ | ----------- |
|  0x1C   | Modbus address |   0   | Value Low       |  Value High  | Confirmation from a write function (Write Single Coil, Write Single Register, Write Multiple Coils, Write Multiple Registers) with the new value |
|  0x1C   | Modbus address |   1   | Modbus register | following 2 bytes after Modbus register | No response from the Modbus device |
|  0x1C   | Modbus address |   2   | Modbus register |    0x0000    | Package had a CRC error |
|  0x1C   | Modbus address |   3   | Modbus register | 16-bit value | Invalid response, e.g. from a different Modbus device or just garbage with a correct CRC |
|  0x1C   | Modbus address |   4   | Modbus register |    0x0000    | Invalid package length |
|  0x1C   | Modbus address |   5   | Modbus register | 16-bit value | Unexpected error, e.g. an unknown function code |
|  0x1C   | Modbus address |   6   |        ?        |       ?      | TX queue overrun (not sure if this one can happen) |
|  0x5C   | Modbus address |   0   | Value Low       |   Value High | The non-error reply contains the requested 32-bit value |

The value is send as a 32-bit value, it is extracted from the Modbus package in this way. `pkt` is the received Modbus package as specified in the Modbus documentation.

- read coils (1), read discrete inputs (2) simply return `pkt[3]`
- read exception status (7) returns `pkt[2]`
- read holding registers (3), read input register (4) checks if combine two registers (bit 13) is set. If so it takes a 32-bit value from `pkt[3-6]`. If the register order (bit 14) is set, then the upper/lower 16-bit are swapped. Then the byte order (bit 15) is applied. If a single 16-bit register is read (bit 13 is cleared), then a 16-bit from `pkt[3-4]` is read and only the byte order (bit 15) need to be applied.
