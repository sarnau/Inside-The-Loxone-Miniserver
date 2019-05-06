# RS485 Extension (`0x07`)

This extension is almost identical to the [RS232 extension](LoxoneLinkLegacyExtensionRS485.md), but even simpler. The RS485 is different from an RS232 mainly by having to enable/disable TX/RX, because the serial lines are a bus.

| Command | Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | -------- | --- | -- | ----- | ----- | ----------- |
|  0x69   | Start    | S→E | config | B1=end character, B2=unused | baud rate | Configure the RS485. config bits 0-1:word length (0:5, 1:6, 2:7, 3:8), bit 2-5: parity (1:even, 2:odd, 3:zero, 4:one), bit 6:stop bits (0:1, 1:2), bit 7:has end character flag |
|  0x71   |          | S→E |    |       |       | Send bytes (see below) |

## Sending bytes

Sending up to 255 bytes works as follows:

1.  Send `0x71` with `B0` = `0x00`. `B1` = length of byte stream, `B2` = CRC8 over the byte stream, `B3`…`B6`: first 4 bytes of the package
2.  Send `0x71` with `(B0 * 6 - 2)` being the offset into the byte stream. `B1`…`B6` are the next 6 bytes of the package

Once the last package necessary is received and the CRC8 is validated, they package is queued for sending. If the CRC8 is not correct, the package is simply ignored.

## Receiving bytes

If an end character is set (e.g. CR), then all received bytes are buffered till this character is detected or the 512 bytes receiving buffer is full. The are send back as a `0x44` fragmented package (see the description in the general legacy extension document) with the type being `0x0A` (RS232 data bytes received).

Without an end character, bytes are send whenever they are available with a little delay to allow avoid sending individual bytes all the time.
