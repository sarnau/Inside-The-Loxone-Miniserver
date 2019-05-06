# AO Extension

The AO Extension is a NAT extension, which one of the most basic ones. It only receives Analog Values `0x81` (the scale factor )

Values are expected between 0V (0) and 10V (1000). The Gamma Correction is the typical square conversion. The values are send from the Miniserver whenever they change or after a NAT was assigned, e.g. after reboot.

Configuration, Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8…11   |     0 | Unused, 0x00000000 |
|  12…15   |     0 | 4 8-bit values with the slew rate in %/s (0 = Jump) |
|  16…19   |     0 | 4 8-bit values with the Gamma Correction/Reception Correction flag (0=OFF, !=0=ON) |
