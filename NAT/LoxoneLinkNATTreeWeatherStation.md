# Weather Station Tree (0x800b)

This device works like the [DI Extension](LoxoneLinkNATExtensionDI.md), but with only 6 inputs instead of 20.

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0       | Warnings    | S←E | Bit 0:Rain, Bit 1:Storm, Bit 2:Sunshine |
| Analog  | 0       | Brightness  | S←E | Value in Lx |
| Analog  | 1       | Windspeed   | S←E | Value in km/h |
| Analog  | 2       | Temperature | S←E | Value in C |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8-9    |    5  | Unknown (unused?) |
|  10-10   |   28  | Unknown (unused?) |
|    12    |   20  | Unknown (unused?) |
|    13    |   80  | Sunshine Threshold |
|    14    |   35  | Storm Warning Threshold (0…150km/h) |
