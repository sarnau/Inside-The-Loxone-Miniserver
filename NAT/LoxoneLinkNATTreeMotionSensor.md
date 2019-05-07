# Motion Sensor Tree (0x8002)

It uses a Max44009 just like the Weather Station Tree to measure the brightness.

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0       | Motion      | S←E | !=0:Motion detected |
| Analog  | 0       | Brightness  | S←E | Value in Lx |
| Analog  | 1       | LED Color   | S→E | Set the color of the LED (0:off, 1:green, 2:orange, 3:red) |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8-11   |    0  | If set, then the Brightness is sent every n minutes |
|    12    |    0  | Sensitivity for Motion Detection (0-3:Low,Medium,High,Maximum) |
|    13    |    0  | Unknown (unused) |
