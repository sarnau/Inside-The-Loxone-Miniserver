# LED Ceiling Light Tree (0x8006)

The LED Ceiling Light Tree is similar the the RGBW 24V Dimmer with a motion sensor and a brightness detector.

The dimming is updated at a fixed frequency of 200Hz.

|         Type    | Index   | Name        | Dir | Description |
| --------------  | ------- | ----------- | --- | ----------- |
|         Digital | 0       | Motion      | S←E | !=0:Motion detected |
|         Analog  | 0       | Brightness  | S←E | Value in Lx |
|            RGBW |         | Light RGBW  | S→E | 4 bytes (RGBW) in value32 for standard devices |
|  Composite RGBW |         | Light RGBW  | S→E | 4 bytes (RGBW) in value32 for smart devices,  |
|            0x8B |         | Light RGBW  | S→E | `B0-B7` contain the Composite RGBW, only executed if `B8-B11` is !=0 and matches the magic value from the config. |

Smart Device have a fade time, which is managed by the device. The fade time is either in 1/10s (bit 14=0) or in seconds (bit 14=1). The standard devices always use the fade rate, but it can be disabled by setting bit 0 to bit 3 in `B1` (for the four RGBW components). If any of the bits 0-2 are set, fading is disabled for RGB. If bit 3 is set, it is disabled for white. So, it can strangely be disabled independently.
 
Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|     8    |    1  | Sensitivity (0-3) |
|        9 | 0…101 | Red: Loss of connection value in % (101% = Retain Last State) |
|       10 | 0…101 | Green: Loss of connection value in % (101% = Retain Last State) |
|       11 | 0…101 | Blue: Loss of connection value in % (101% = Retain Last State) |
|       12 | 0…101 | White: Loss of connection value in % (101% = Retain Last State) |
|       13 | 0…100 | Red: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       14 | 0…100 | Green: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       15 | 0…100 | Blue: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       16 | 0…100 | White: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|    17-20 | long  | magic value |
