# Damper Tree (0x8013)

This device has the same commands and configuration as the [Valve Actuator Tree](LoxoneLinkNATTreeValveActuator.md)

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Analog  | 0x00    | Percent     | S←E | Valve position in percent (0…100%) |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|     8    |   101 | 0…100: Loss of Connection Value, 101:Retain Last State |
