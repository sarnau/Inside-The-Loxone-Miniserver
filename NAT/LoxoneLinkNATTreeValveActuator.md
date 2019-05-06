# Valve Actuator Tree (0x8001)

This device has the same commands and configuration as the [Damper Tree](LoxoneLinkNATTreeDamper.md)

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Analog  | 0x00    | Percent     | S←E | Valve position in percent (0…100%) |

Configuration Version 2:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|     8    |   101 | 0…100: Loss of Connection Value, 101:Retain Last State |
