# Nano DI Tree (0x800b)

This device works like the [DI Extension](LoxoneLinkNATExtensionDI.md), but with only 6 inputs instead of 20.

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | Inputs      | S←E | Bitmask with the 6 possible inputs  |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8…9    |     0 | Bitmask for frequency-enabled inputs |
