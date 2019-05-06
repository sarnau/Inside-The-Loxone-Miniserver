# Room Comfort Sensor Tree (0x8010)

The Room Comfort Sensor is build around the SHT21 (Temperature and Humidity) and the CCS811 Air Quality Sensor. It requires a burn-in time of several hours to have stable results. It does not actually measure CO2, but an "equivalent CO2" value.

| Type    | Index   | Name        | Dir | Description |
| ------  | ------- | ----------- | --- | ----------- |
| Digital | 0x00    | CO2 status  | S←E | 1:CO2<1500, 2:CO2<=2500, 4:CO2>2500 (unused in Loxone Config) |
| Analog  | 0x00    | Temperature | S←E | Temperature in Celcius * 100.0, sent every n minutes or if temperature changes >1deg |
| Analog  | 0x01    | Humidity    | S←E | Humidity in Percent * 100.0, sent every n minutes or if humidity changes >20% |
| Analog  | 0x02    | CO2 value   | S←E | CO2 value, send every n minutes and if CO2 changes >100, error bits:6:CO2>5000, 7:burn in phase still active |
| Analog  | 0x03    | CO2 warning | S←E | 1:CO2<1500, 2:CO2<=2500, 3:CO2>2500 (unused in Loxone Config) |

Configuration Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|  8…11    |    15 | Time interval for sending temperature and humidity in minutes |
