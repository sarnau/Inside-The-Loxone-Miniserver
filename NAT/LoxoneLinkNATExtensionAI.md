# AI Extension

The AI Extension is a NAT extension, which one of the most basic ones. It only sends only messages Analog Value `0x81`.

The analog inputs are send back whenever the values changes. Values are between 0V (0) and 10V (10000), they have a 12-bit resolution. The scaling factor is 5 (see the general NAT Protocol documentation), which means the Miniserver divides it by 1000 to generate an analog value from 0.0V to 10.00V.

They are either send back, when forced or when a value changes. The amount of changes needed is determined by the configuration: delta between the current value and the last send value has to be larger then the threshold value. If that is the case, it is throttled to send only one change per "Minimal Time Space".

Alternatively it is possible to average values over time by setting the "Mean Value Calculation Time". In this case a value is sampled at 100Hz and every n seconds it is divided by the number of samples to generate an average.

Like all NAT extensions, it does send the current state of the inputs back to the Miniserver after a NAT was received.

Configuration, Version 1:

| Offset   | Value | Description |
| -------- | ----- | ----------- |
|   8…23   |     0 | 4 32-bit Threshold values in mV |
|  24…39   |     0 | 4 32-bit Minimal Time Space values in ms |
|  40…47   |     0 | 4 16-bit Mean Value Calculation Times in seconds |
