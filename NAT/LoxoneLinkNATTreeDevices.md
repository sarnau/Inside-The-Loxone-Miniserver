# Tree Devices

## Valve Actuator Tree / Damper Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Analog  | 0x00    | Percent     | S←E | Valve position in percent (0…100%) |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|     8    |   101 | 0…100: Loss of Connection Value, 101:Retain Last State |

## Motion Sensor Tree

| Type    | Index   | Name       | Dir | Description |
| ------  | ------- | ---------- | --- | ----------- |
| Digital | 0x00    | Motion     | S←E | Motion detected (==1, resets to 0 after about 3 seconds) |
| Analog  | 0x00    | Brightness | S←E | Brightness in Lx, sent when the value changes, which can happen about every ~1.5s |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|          |       |             |

02ff00840300000f000000010000000000


## Touch Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | Touch       | S←E | Button touched, 5-bits for the 5 different touch zones (Top-Left, Top-Right, Center, Bottom-Left, Bottom-Right), multiple buttons are possible  |
| Analog  | 0x00    | Temperature | S←E | Temperature in Celcius, sent every 10 minutes and after startup |
| Analog  | 0x01    | Humidity    | S←E | Humidity in Percent, sent every 10 minutes and after startup |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|  8…11    |    15 | Unknown |
|   12     |   1/0 | Audible Acknowledgement on/off |


## Touch Pure Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | Touch       | S←E | Button touched, 5-bits for the 5 different touch zones (Top-Left, Top-Right, Center, Bottom-Left, Bottom-Right)  |
| Digital | 0x00    | Backlight   | S→E | Backlight output on/off  |
| Analog  | 0x00    | Temperature | S←E | Temperature in Celcius, sent every 10 minutes and after startup |
| Analog  | 0x01    | Humidity    | S←E | Humidity in Percent, sent every 10 minutes and after startup |

TODO: backlight output, probably digital 0x01

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|  8…11    |    15 | Unknown |
|   12     |   1/0 | Audible Acknowledgement on/off |


## Nano DI Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | Inputs      | S←E | Bitmask with the 6 possible inputs  |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8…9    |     0 | Bitmask for frequency-enabled inputs |


## LED Surface Mount Spot RGBW/WW Tree, LED Spot RGBW/WW Tree Gen 1/2, LED Pendulum Slim RGBW Tree, RGBW 24V Dimmer Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Composite RGBW | 0x00 | Smart Actuator | S←E | Light settings with RGBW in value32 |

Standard Device with two actuators:
Dimmer RGB: RGB=RGB from value32, WW=0
Dimmer WW: RGB=0, WW=W from value32

Standard Device with 4 individual channels:
Changes in the same cycle will be transmitted as one message!

Smart Device:
Smart Actuator RGBW: RGBW in value32, Fade Time in value16 in 1/10s

Smart Device with 4 individual channels:
0x8a Composite White Values:0,80,0,0 FadingTimes:2560,0,0,0>


Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|        0 | 0…101 | Red: Loss of connection value in % (101% = Retain Last State) |
|        1 | 0…101 | Green: Loss of connection value in % (101% = Retain Last State) |
|        2 | 0…101 | Blue: Loss of connection value in % (101% = Retain Last State) |
|        3 | 0…101 | White: Loss of connection value in % (101% = Retain Last State) |
|        4 | 0…100 | Red: Fade Rate in % (0%=Jump), Bit 7: Perception correction active |
|        5 | 0…100 | Green: Fade Rate in % (0%=Jump), Bit 7: Perception correction active |
|        6 | 0…100 | Blue: Fade Rate in % (0%=Jump), Bit 7: Perception correction active |
|        7 | 0…100 | White: Fade Rate in % (0%=Jump), Bit 7: Perception correction active |
|        8 |       | Red: Output type (27=RGB, 35=Red, 36=Green, 37=Blue, 38=WW, 158=Smart RGBW, 159=Smart Red, 160=Smart Green, 161=Smart Blue, 162=Smart WW) |
|        9 |       | Green: Output type (27=RGB, 35=Red, 36=Green, 37=Blue, 38=WW, 158=Smart RGBW, 159=Smart Red, 160=Smart Green, 161=Smart Blue, 162=Smart WW) |
|       10 |       | Blue: Output type (27=RGB, 35=Red, 36=Green, 37=Blue, 38=WW, 158=Smart RGBW, 159=Smart Red, 160=Smart Green, 161=Smart Blue, 162=Smart WW) |
|       11 |       | White: Output type (27=RGB, 35=Red, 36=Green, 37=Blue, 38=WW, 158=Smart RGBW, 159=Smart Red, 160=Smart Green, 161=Smart Blue, 162=Smart WW) |

Smart devices do not use the fade rate from the configuration (it is set to "Jump" and perception correction is always active)

## LED Ceiling Light Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Composite RGBW | 0x00 | Smart Actuator | S←E | Light settings |

Brightness & Motion input and configuration!

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|          |       |             |

01656565650000000000000000

## Leaf Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | ?           | S→E | ? |
| Analog  | 0x00    | ?           | S→E | ? |
| Analog  | 0x01    | ?           | S→E | ? |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8…11   |  2200 | Filter change interval in hours |


## Room Comfort Sensor Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | CO2 status  | S←E | 1:CO2<1500, 2:CO2<=2500, 4:CO2>2500 (unused in Loxone Config) |
| Analog  | 0x00    | Temperature | S←E | Temperature in Celcius, sent every 10 minutes and if temp changes >1deg |
| Analog  | 0x01    | Humidity    | S←E | Humidity in Percent, sent every 10 minutes and if hum changes >20% |
| Analog  | 0x02    | CO2 value   | S←E | CO2 value, send every 15 minutes and if CO2 changes >100, error bits:6:CO2>5000, 7:burn in phase still active |
| Analog  | 0x03    | CO2 warning | S←E | 1:CO2<1500, 2:CO2<=2500, 3:CO2>2500 (unused in Loxone Config) |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|  8…11    |    15 | Unknown |


## Alarm Siren Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | Tamper Contact | S←E |  |
| Digital | 0x00    | Alarm       | S←E | Bit 0:Strobe Light, Bit 1:Alarm Sound |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8      |    0  | Unknown |
|   9…10   |  120  | Maximum audible alarm duration in seconds (0=no limit, 1-1800s) |

Tamper Contact has a special case, because after reboot it triggers. This means the Alarm Siren needs to have some communication.


## Weather Station Tree

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | ?       | ?           | S←E | |
| Digital | ?       | ?           | S←E | |
| Digital | ?       | ?           | S←E | |
| Analog  | ?       | ?           | S←E | |
| Analog  | ?       | ?           | S←E | |
| Analog  | ?       | ?           | S←E | |

Analog values: Brightness, Wind Speed, Temperature
Digital values: Rain, Storm Warning, Sunshine

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|     8    |    5  | Unknown |
|     9    |    0  | Unknown |
|    10    |   28  | Unknown |
|    11    |    0  | Unknown |
|    12    |   20  | Unknown |
|    13    |   80  | Sunshine Threshold |
|    14    |   35  | Storm Warning Threshold (0…150km/h) |

## NFC Code Touch Tree

Uses an encrypted communication, this device should be on a dedicated Tree branch, otherwise the encryption would be kind of useless, because a hacker could inject the door open messages directly.

## Touch Surface Tree

Like a Touch Pure Tree, but with an additional input and options (Activiation required, use activation LEDs, a timeout [1-20s, 5s] and a calibration, controlled via WebRequests, like 'GetCalibration/60')

## Universal Tree

An unreleased Loxone Extension for the Tree bus with 4 analog inputs, 4 analog outputs, 8 digital inputs and 8 relays.

These are somehow not stored in the config, which is version 2 with 00000000000000000000000000000000

## Integrated Window Contact Tree

An unreleased door handle, which is currently only available as an Air device.



## AI Extension




## AO Extension

000000000023640101000000

