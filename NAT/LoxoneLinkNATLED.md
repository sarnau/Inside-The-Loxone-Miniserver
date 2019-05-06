# Various LED devices

All LED devices seem to share the same protocol, so I document them all in one document.

- LED Surface Mount Spot RGBW Tree (0x8007)
- LED Surface Mount Spot WW Tree (0x800e)
- LED Spot RGBW Tree Gen 1 (0x8008)
- LED Spot WW Tree Gen 1 (0x800f)
- LED Spot RGBW Tree (0x8016)
- LED Spot WW Tree (0x8017)
- LED Pendulum Slim RGBW Tree (0x8011)

The dimming is updated at a fixed frequency between 123Hz and 1kHz. It seems the frequency can not be changed, but the software would support that.


|           Type | Dir | Description |
| -------------- | --- | ----------- |
|           RGBW | S→E | 4 bytes (RGBW) in value32 for standard devices |
| Composite RGBW | S→E | 4 bytes (RGBW) in value32 for smart devices |

Standard Device with two actuators:
Dimmer RGB: RGB=RGB from value32, WW=0
Dimmer WW: RGB=0, WW=W from value32

Standard Device with 4 individual channels:
Changes in the same cycle will be transmitted as one message!

Smart Device have a fade time, which is managed by the device. The fade time is either in 1/10s (bit 14=0) or in seconds (bit 14=1). The standard devices always use the fade rate, but it can be disabled by setting bit 0 to bit 3 in `B1` (for the four RGBW components). If any of the bits 0-2 are set, fading is disabled for RGB. If bit 3 is set, it is disabled for white. So, it can strangely be disabled independently.


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

Smart devices do not use the fade rate from the configuration (it is set to "Jump" and perception correction is always active), because the fade is transmitted with each command.
