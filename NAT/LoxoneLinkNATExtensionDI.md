# DI Extension (0x14)

The DI Extension is a NAT extension, which one of the most basic ones. It only sends only two messages Digital Value `0x80` and Frequency `0x85`.

The 20 digital inputs are send back up to 50x per second, whenever one of the input changes. Each input can be configured to measure frequencies instead. Frequency values are measured in Hz and are simply counting flank changes per second (0→1). They are reported once per second, if the frequency is != 0 Hz. 0Hz is only send once.

Like all NAT extensions, it does send the current state of the inputs back to the Miniserver after a NAT was received. The frequency inputs are not send, because they are send every second anyway.

Configuration, Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8…11   |     0 | Bitmask for frequency-enabled inputs |
