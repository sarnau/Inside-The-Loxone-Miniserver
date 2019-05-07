# RGBW 24V Dimmer Tree (0x800c)

The RGBW 24V Dimmer has some additional special cases vs the standard [LED devices](LoxoneLinkNATLED.md)

The dimming is updated at a fixed frequency of 123Hz. It seems the frequency can not be changed, but the software would supports a range between 123Hz and 1kHz


|            Type | Dir | Description |
| --------------- | --- | ----------- |
|            RGBW | S→E | 4 bytes (RGBW) in value32 for standard devices |
|  Composite RGBW | S→E | 4 bytes (RGBW) in value32 for smart devices |
| Composite White | S→E | A fragmented package with RGBW in `B2-B5` and the 16-bit fade time values for 4 components in `B6-B13`. `B0-B1` and `B14-B15` are unused. |

Standard Device with two actuators:
Dimmer RGB: RGB=RGB from value32, WW=0
Dimmer WW: RGB=0, WW=W from value32

Standard Device with 4 individual channels:
Changes in the same cycle will be transmitted as one message!

Smart Device have a fade time, which is managed by the device. The fade time is either in 1/10s (bit 14=0) or in seconds (bit 14=1). The standard devices always use the fade rate, but it can be disabled by setting bit 0 to bit 3 in `B1` (for the four RGBW components).

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|        8 | 0…101 | Red: Loss of connection value in % (101% = Retain Last State) |
|        9 | 0…101 | Green: Loss of connection value in % (101% = Retain Last State) |
|       10 | 0…101 | Blue: Loss of connection value in % (101% = Retain Last State) |
|       11 | 0…101 | White: Loss of connection value in % (101% = Retain Last State) |
|       12 | 0…100 | Red: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       13 | 0…100 | Green: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       14 | 0…100 | Blue: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       15 | 0…100 | White: Fade Rate in % (0%=Jump), Bit 7: Gamma/Perception correction active |
|       16 | byte  | Red: RGB Actuator Type |
|       17 | byte  | Green: RGB Actuator Type (unused) |
|       18 | byte  | Blue: RGB Actuator Type (unused) |
|       19 | byte  | White: RGB Actuator Type (unused) |

Smart devices do not use the fade rate from the configuration (it is set to "Jump" and perception correction is always active), because the fade is transmitted with each command.

The possible values for the RGB Actuators are:

| Value | Type |
| ----- | ---- |
|    27 | Standard RGBW |
|    35 | Standard Red |
|    36 | Standard Green |
|    37 | Standard Blue |
|    38 | Standard White |
|   158 | Smart RGBW |
|   159 | Smart Red |
|   160 | Smart Green |
|   161 | Smart Blue |
|   162 | Smart White |
