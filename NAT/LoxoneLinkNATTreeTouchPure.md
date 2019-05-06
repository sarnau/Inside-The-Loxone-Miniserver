# Touch Pure Tree (0x8005)

| Type    | Index   | Name             | Dir | Description |
| ------  | ------- | ---------------- | --- | ----------- |
| Digital | 0x00    | Touch            | S←E | Button touched, 5-bits for the 5 different touch zones (1:Top-Left, 2:Top-Right, 4:Center, 8:Bottom-Left, 16:Bottom-Right), multiple buttons are possible.  |
| Digital | 0x00    | Backlight/Buzzer | S→E | Bit 0:Backlight output on/off, Bit 1:Buzzer on/off |
| Analog  | 0x00    | Temperature      | S←E | Temperature in Celcius, sent every n minutes and after startup. Signed value multiplied by 1000.0 (scaling factor 5). |
| Analog  | 0x01    | Humidity         | S←E | Humidity in Percent, sent every n minutes and after startup. Signed value multiplied by 1000.0 (scaling factor 5). |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|  8…11    |     1 | Send interval for temperature and humidity in minutes |
|   12     |   1/0 | Audible Acknowledgement on/off |
