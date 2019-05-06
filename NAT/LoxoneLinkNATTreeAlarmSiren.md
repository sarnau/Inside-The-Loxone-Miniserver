# Alarm Siren Tree (0x8012)

The Alarm Siren seems to be a modified version of the [Satel SP-4002 R](https://www.satel.pl/en/product/245/SP-4002%20R,Outdoor-siren-with-optical-and-acoustical-signaling-(battery-back-up)) with the added Tree Bus and a temperature sensor.

Tamper contact is a special case, because it not only continuously tests the tamper contact and immediately reports any changes back to the Miniserver, it also sends the current state of the tamper contact back to the server every 30s. If the server notices that the message was missing, it will also trigger an alarm.

The siren also has a STS21 temperature sensor and reports the current temperature back every 5 minutes, but this feature seems currently not being used.

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | Tamper Contact | S←E |  |
| Digital | 0x00    | Alarm       | S→E | Bit 0:Strobe Light, Bit 1:Alarm Sound |
| Analog  | 0x00    | Alarm       | S←E | Current Temperature in Celcius * 100 |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8      |    0  | Offline state behavior |
|   9…10   |  120  | Maximum audible alarm duration in seconds (0=no limit, 1-1800s) |

If the Alarm Siren gets offline, e.g. the Tree Bus gets disconnected, it can do the following things, based on the configuration:

- 1: turn on the strobe light
- 2: turn off the strobe light
- 4: turn on the siren (respecting the maximum duration)
- 8: turn off the siren
