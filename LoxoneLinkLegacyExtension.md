# Extension (`0x01`)

The extension sends the status of its inputs and outputs in a separate thread, so there can be a little delay between setting the e.g. relay outputs and receiving the response.

| Command | Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | -------- | --- | -- | ----- | ----- | ----------- |
|  0x04   | Start    | S←E |    | bitmask | version | Acknowledge the configuration |
|  0x10   | Start    | S→E | top bits | bitmask | lower bits | Set analog input sensitivity for inputs #1 and #2 |
|  0x11   | Start    | S→E | top bits | bitmask | lower bits | Set analog input sensitivity for inputs #3 and #4 |
|  0x20   |          | S←E | top bits | 0x0000 | lower bits | Returns the status of the 4 analog inputs. See 'Analog value package' below for details |
|  0x30   |          | S↔E | top bits | 0x0000 | lower bits | Set or returns the status of the 4 analog outputs. See 'Analog value package' below for details |
|  0x31   | Start    | S→E | top bits | bitmask | lower bits | Set analog output configuration for outputs #1-#4. See 'Analog output configuration' below for details |
|  0x40   | Start    | S→E | top bits | bitmask | lower bits | Set digital input configuration for inputs #1-#4 |
|  0x41   | Start    | S→E | top bits | bitmask | lower bits | Set digital input configuration for inputs #5-#8 |
|  0x42   | Start    | S→E | top bits | bitmask | lower bits | Set digital input configuration for inputs #9-#12 |
|  0x50   |          | S←E |    |      | val32 | Return the status of the 12 digital inputs. |
|  0x51   |          | S←E |    |      |       | Return the frequency values of digital inputs. See 'Digital frequency input' |
|  0x60   |          | S↔E |    |       |       | Set or return the status of the 14 output relays. |
|  0x53   | Idle     | S←E | XX | YYYY | temperature | Overheating warning from an extension, as described in the Overheating protection section in the documentation for the Link Legacy format. |

## Confirm configuration via bitmask
The extension confirms the successful configuration back to the Miniserver. This is controlled by the 16 bit `bitmask` parameter in the commands `0x10/0x11` and `0x40/0x41/0x42`.

The `bitmask` works as follows:
- If bit 15 is set, the lower 14 bits are simply stored in a variable in the extension.
- If bit 15 is cleared, the lower 14 bits are or'ed to this variable.
- If bit 14 is set, a `0x04` configuration acknowledge command will be send with `B1/B2` containing the lower 14 bits of this variable and `B3-B6` containing the firmware version. This allows the Miniserver to validate, that all configuration commands where received by the extension.

This is what actually happens with the current Miniserver:
- `0x10` sends a `0x8001` bitmask
- `0x11` sends a `0x0002` bitmask
- `0x40` sends a `0x0004` bitmask
- `0x41` sends a `0x0008` bitmask
- `0x42` sends a `0x4010` bitmask. This results a bitmask of 0x001F to be send back to the Miniserver.

Triggering sending the `0x04` configuration acknowledge package back is also followed by sending the frequencies, analog input status and digital input status back to provide actual values to the Miniserver.

## Analog value package

Analog values are 10 bit values (0-1023) or 0V-10V. 4 values in a package are stored as such:

value #1: `B3 + ((B0 & 0x03) << 8)`
value #2: `B4 + ((B0 & 0x0C) << 6)`
value #3: `B5 + ((B0 & 0x30) << 4)`
value #4: `B6 + ((B0 & 0xC0) << 2)`

## 10 bit time encoding

Certain parameters allow a time duration or delay. To store a large range in a 10 bit value, the following encoding is used: the top 7 bits are the base value. This value is then multiplied by a factor based on the lower 3 bits. The following factors are possible:

- 0 = `1` (milliseconds)
- 1 = `10` (10 milliseconds)
- 2 = `100` (100 milliseconds)
- 3 = `1000` (seconds)
- 4 = `10*1000` (10 seconds)
- 5 = `60*1000` (minutes)
- 6 = `10*60*1000` (10 minutes)
- 7 = `60*60*1000` (hours)

On encoding Loxone Config tries to match a time as closely as possible to the requested value. With this encoding a 10-bit value can be used from single milliseconds up to 127 hours! It's a bit like a poor man floating point number with the factor being the exponent.

## Analog input configuration

2 inputs are configured with one package, so 2 packages are needed to configure all 4 inputs.

- Input #1: p1=`B3 + ((B0 & 0x03) << 8)`, p2=`B4 + ((B0 & 0x0C) << 6)`
- Input #2: p1=`B5 + ((B0 & 0x30) << 4)`, p2=`B6 + ((B0 & 0xC0) << 4)`

Parameter `p1` is the minimal change (0..999 around the read value, equivalent to 0.0…99.9%) _or_ the average (1001:1min, 1002:5min, 1003:10min, 1004:30min, 1005:60min, 1006:1s, 1007:5s, 1008:10s, 1009:30s) - only one option is possible in Loxone Config.

Parameter `p2` is the minimum time interval, encoded as mentioned above in '10 bit time encoding'

## Analog output configuration

The analog outputs are configured with one package:

- Output #1: p1=`(B1 & 0x0F) >> 0`, p2=`B3 & 0x1F`
- Output #2: p1=`(B1 & 0xF0) >> 4`, p2=`B4 & 0x1F`
- Output #1: p1=`(B2 & 0x0F) >> 0`, p2=`B5 & 0x1F`
- Output #2: p1=`(B2 & 0xF0) >> 4`, p2=`B6 & 0x1F`

Parameter `p1` enables the perception correction (4 = off, otherwise on). The perception table is just the input values squared.

Parameter `p2` is the fade rate (0 = Jump, 1…20: in 5% steps, 21=1%, 22=2%, 23…31=undefined, unused).

The extension sends this configuration command back to the Miniserver to confirm (with bit 7 set in the command byte)

## Digital input configuration

4 inputs are configured with one package, so 3 packages are needed to configure all 12 inputs.

- Input #1: `B3 + ((B0 & 0x03) << 8)`
- Input #2: `B4 + ((B0 & 0x0C) << 6)`
- Input #3: `B5 + ((B0 & 0x30) << 4)`
- Input #4: `B6 + ((B0 & 0xC0) << 2)`

The values are the minimum time interval, encoded as mentioned above in '10 bit time encoding'. The special case is 1023, which means the input is used as a frequency counter.

## Digital frequency input

Technically all 12 digital inputs support frequency measurements. Up to four frequency values can be send in one package.

- `B0`,`B1`,`B2`,`B3` are the frequency in Hz (0…150Hz are supported)

These values are assigned to 4 inputs, which are provided in `(B4 & 0x0F)`, `(B4 >> 4)`, `(B5 & 0x0F)`, `(B5 >> 4)`. The input is 0…11 for the 12 inputs or the value of 15, if the frequency value is unused and should be ignored.
