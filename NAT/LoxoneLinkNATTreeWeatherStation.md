# Weather Station Tree (0x800b)

The Weather Station collects certain local weather information and forwards them to the server.

For the Brightness and Sunshine it uses a Max44009 just like the Motion Sensor Tree. Temperature is measured with a STS21. Rain via a circuit that detects moisture. Wind is done via a counter, which measures the rotation speed.

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
|  10-10   |   28  | Brightness Sunshine Threshold in 1000Lx |
|    12    |   20  | Unknown (unused?) |
|    13    |   80  | Unknown (unused?)  |
|    14    |   35  | Storm Warning Threshold (0…150km/h) |
