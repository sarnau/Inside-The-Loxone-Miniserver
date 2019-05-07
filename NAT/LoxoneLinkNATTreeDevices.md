# Tree Devices

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

## NFC Code Touch Tree

Uses an encrypted communication, this device should be on a dedicated Tree branch, otherwise the encryption would be kind of useless, because a hacker could inject the door open messages directly.

## Touch Surface Tree

Like a Touch Pure Tree, but with an additional input and options (Activiation required, use activation LEDs, a timeout [1-20s, 5s] and a calibration, controlled via WebRequests, like 'GetCalibration/60')

## Universal Tree

An unreleased Loxone Extension for the Tree bus with 4 analog inputs, 4 analog outputs, 8 digital inputs and 8 relays.

These are somehow not stored in the config, which is version 2 with 00000000000000000000000000000000

## Integrated Window Contact Tree

An unreleased door handle, which is currently only available as an Air device.
