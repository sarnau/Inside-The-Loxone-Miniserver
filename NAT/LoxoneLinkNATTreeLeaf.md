# Leaf Tree (0x8014)

| Type    | Index   | Name             | Dir | Description |
| ------  | ------- | ---------------- | --- | ----------- |
| Digital | 0x00    | Flags            | S→E | Bit 0:Confirm Filter Changed, Bit 1:unknown |
| Digital | 0x00    | Error Flags      | S←E | Bit 0:Filter Warning active, Bit 1:Fan Fault, Bit 2:Aperture Fault |
| Analog  | 0x00    | Mode             | S→E | Operation mode (0=off, 1=Airing phase, 2=Supply fresh air, 3=Exhaust) |
| Analog  | 0x01    | Speed            | S→E | Speed of the fan in % (0-100). |


Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|  8…11    |  2200 | Filter change interval in hours |
| 12…15    |     0 | Time Offset (unknown) |
|   16     |     0 | direction Index (flag for the direction of the fan?) |
