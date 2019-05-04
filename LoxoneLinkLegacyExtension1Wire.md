# 1-Wire Extension (`0x05`)

The 1-Wire Extension supports up to 32 1-Wire devices and supports 3 different family categories:

1. Temperature sensors: DS18S20, DS1822 and DS18B20 (Family codes 0x10, 0x22, 0x28)
2. Smart battery monitor: DS2438 (Family code 0x26)
3. other devices just as iButton (arrive/depart) (Family codes 0x01, 0x02, 0x04, 0x06, 0x08, 0x09, 0x0B, 0x0C, 0x0F, 0x14, 0x18, 0x1A, 0x21, 0x23, 0x24, 0x37 and 0x41)

That said, it seems the Miniserver doesn't support them all. It does seem to support the DS18S20 and the DS18B20 for temperature and DS2438 for temperature and voltage. And DS2401, DS1963S and DS1922 for iButton.

It uses a DS2480 to communicate with the 1-Wire bus.

| Command | Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | -------- | --- | -- | ----- | ----- | ----------- |
|  0x1D   |          | S→E |    |       |       | `B0`==0:Request 1-Wire statistics, `B0`==1:Reset 1-Wire statistics |
|  0x63   |          | S→E | Family code |       | polling cycle | Set polling cycle for certain families, seem to be ignored by the 1-Wire Extension |
|  0x64   |          | S→E |    |       |       | `B1` != 0: force iButton update on/off via `B0`, `B1`==0: scan for 1-Wire devices |

## Configuration

The 1-Wire extension has its settings stored in FLASH. It is uploaded via a fragmented message with the type `0x06` from the Miniserver and updates are only send, if necessary (see `0x36` message above).

Format of the settings, which are 0x14E bytes large:

| Offset |  Type  | Description |
| -----: | :----: | :---------- |
|      0 | 32-bit | 0xFEEDFEED = magic to detect that the package is valid |
|      4 | 16-bit | Version of the settings, always 1 |
|      6 | 16-bit | iButton polling time in ms, 0 = 100ms |
|      8 | 16-bit | Number of 1-Wire devices in the following table |
|   0x0A | 32 * 10 bytes | Up to 32 1-Wire Identifiers, the family code is in the first byte of the 8-byte identifier. It is followed by a 16-bit polling cycle time in seconds. |
|  0x14A | 32-bit | 0x00000000, filler value |

## Request statistics

The 1-Wire Extension collects statistic information about all known devices, especially error stats. They can be reported back, if Loxone Config requests it.

It sends 3 `0x1D` packages back **per** 1-Wire device. All packages have `B0`=2, except the very last one which sets `B0`=3 telling the Miniserver the statistics are complete. The statistics only seem to be collected for temperature sensors.

1. `val32` contains the overall packages requested
2. `val32` contains the CRC errors
3. `val32` contains the 85 Degree Problems errors

## Scan for 1-Wire devices

The 1-Wire bus is polling for all devices. The first 32 are returned. If none are found, only `0x65` is send back with `B0-B6` be zero.

| Command | Description |
| ------- | ----------- |
|  0x64   | Device found. `B0-B6` contain the first 7 bytes of the 1-Wire identifier (byte 8 is the CRC and can be reconstructed) |
|  0x65   | Last Device found. `B0-B6` contain the first 7 bytes of the 1-Wire identifier (byte 8 is the CRC and can be reconstructed) |

## Polling

All 1-Wire devices are managed via polling and value/state changes are then reported back to the Miniserver. There is not direct communication from the Miniserver to the 1-Wire devices supported.

The following commands are send to the Miniserver:

| Command | Description |
| ------- | ----------- |
|  0x63   | iButton init – previously unknown iButton detected, `val32` contain the version number of the extension, `val16` is zero. |
|  0x66   | Temperature and Voltage. `B0`:index of the 32 1-Wire devices, the rest is depended on the family type, see below |
|  0x7A   | iButton sensor arrived (detected). `B0-B6` contain the first 7 bytes of the 1-Wire identifier (byte 8 is the CRC and can be reconstructed) |
|  0x7B   | iButton sensor departed (removed). `B0-B6` contain the first 7 bytes of the 1-Wire identifier (byte 8 is the CRC and can be reconstructed) |

The `0x66` command for temperature and voltage is decoded as follows:

| Sensor      | Conversion |
| :---------: | :--------- |
| DS18S20     | TempCelcius=`B1 + B2 / 128` (`B1` is a signed byte) |
| DS18B20     | TempCelcius=`B1 + B2 / 16.0` (`B1` is a signed byte) |
| DS2438      | TempCelcius=`B2 + (B1>>3)/32.0` (`B2` is a signed byte); VAD=`(B3 + ((B4 & 0x03)<<8))/100.0`; VDD=`(((B5 & 0x0F) << 6) + (B4 >> 2))/100.0`; VSens=`(B6<<4)+(B5>>4)`  (`B6` is a signed byte) |
