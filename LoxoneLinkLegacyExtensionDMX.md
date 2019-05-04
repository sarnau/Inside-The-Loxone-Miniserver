# DMX Extension (`0x04`)

The DMX extension continuously sends 513 bytes packages out, just as DMX-512 requires. The start code (0x00) followed by the 512 DMX channel 8-bit values. A DMX device can have multiple channels (RGBW needs 4). From an electrical standpoint DMX is an RS485 bus with a fixed 250kbit baudrate.

The DMX Extension also uses DMX RDM to find Loxone 24V RGBW Dimmers automatically.

It is up to the DMX extension to handle the fading (via the slewrate) and applies and optional gamma correction, called 'Perception Correction' in Loxone Config. The gamma correction is quite simple:

    result=(value*value)/255


## Additional commands

| Command |      Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | ------------- | --- | -- | ----- | ----- | ----------- |
|  0x08   | Loxone Config | S→E |    |       |       | Identity LED. `val16` contains the Manufacturer Id, `val32` the Device Id, which allows identifying DMX devices. If one of the values is 0, then the DMX Extension will identify itself. |
|  0x64   |               | S→E |    |       |       | Search for DMX devices (see below) |
|  0x74   |               | S→E |    |       |       | Learn DMX, Channel:`B0+(B1<<8)` (1-512), Value:`B2` (0xFF:full brightness, Loxone Config only uses this value) |

## Searching for DMX devices

On request from Loxone Config DMX devices can be search automatically. This is done via DMX RDM, which is vendor agnostic, but the Loxone DMX extension only reports devices with their own manufacturer id (0x2637). Loxone Config does not have that restriction, so a different DMX extension could detect other vendors as well.

The extensions sends back one package per detected DMX device with the DMX UID in the first 6 bytes (`B0-B3` = DeviceId, `B4-B5` = Manufacturer ID). `B6` contains the low byte of the (DMX channel - 1). DMX channels are numbered from 1–512, but reported back as 0-511.

| Command | Description |
| ------- | ----------- |
|  0x12   | DMX device with a channel <= 256 |
|  0x13   | DMX device with a channel <= 256, no more devices |
|  0x64   | DMX device with a channel > 256 |
|  0x65   | DMX device with a channel > 256, no more devices |

If no DMX devices are detect at all, a `0x65` command is send back with an empty package (`B0-B6` are all `0x00`)

## Setting a DMX device

The DMX devices are all controlled via fragmented messages, as described in the legacy extension protocol document.

| fragment type | Name |
| :-----------: | :---------- |
|       `0x0D`  | DMX Send Actor |
|       `0x0E`  | DMX Send Dimming |
|       `0x0F`  | DMX Init RDM Device |
|       `0x13`  | DMX Send Composite Actor |

### Actor Types

The type is in most set package and has the following values:

|   Type | Name |
| -----: | :---------- |
|      0 | Standard White (1 channel) |
|      1 | Standard RGB (3 channels) |
|      2 | Standard RGBW (4 channels) |
|      3 | Standard Lumitech |
|      8 | Smart White (1 channel) |
|      9 | Smart RGB (3 channels) |
|     10 | Smart RGBW (4 channels) |
|     11 | Smart Lumitech |

### Send Actor Package (Standard Actors)

This package is send for standard actors only.

| Offset | Name |
| -----: | :---------- |
|      0 | Type (see above) |
|      1 | Slewrate (0…100: in %/s), Bit 7:Gamma is active |
|    2-3 | Channel minus 1 (range:0-511) |
|    4-7 | Data for up to 4 DMX channels |

Data contains the following, all are scaled in the range 0 (0%) to 255 (100%).

- Standard White : Data[0] = white value
- Standard RGB : Data[0]=red, Data[1]=green, Data[2]=blue
- Standard RGBW : Data[0]=red, Data[1]=green, Data[2]=blue, Data[3]=white
- Standard Lumitech is more complicated, because it supports two modes: RGB and Dual-White. They always use 4 DMX channels.

    Data[0] = 20 => Lumitech Dual White
    Data[1] = Brightness
    Data[2] = Color temperature in Kevin Range (scaled from 0=2700K to 255=6500K)
    Data[3] = unused

    Data[0] = 101 => Lumitech RGB
    Data[1] = Red
    Data[2] = Green
    Data[3] = Blue

Because all values are scaled by the Miniserver into the 0-255 range, it can be tricky to send specific values to a DMX device, which might be necessary to select a specific function. There is an undocumented trick: select the source value high to 777777 and the destination value also to 777777 in Loxone Config. With these magic values, the Miniserver will send the value as-is in Data[0]! As you can see this only withs with a Standard White actor, because multiple channels are not supported.

### Send Dimming Package (Standard Actors)

This function is identical to "Send Actor", except that the Device Id is tested. If the top 4 bits are `0xD`, then the Slewrate is reset to 0. Current Loxone 24V RGBW Dimmers have `0xE` in the top 4 bits. I can only assume that at some point a dimmer without support for a Slewrate existed.

| Offset | Name |
| -----: | :---------- |
|      0 | Send Actor Package (see above) |
|   8-11 | Device Id |

### Init RDM Device

Configures DMX device via RDM by sending a SET 'DMX START ADDRESS'. Only sends to the Loxone Manufacturer ID. The extension tries to send this RDM command 3 times. The Miniserver does not get a response from this command.

| Offset | Name |
| -----: | :---------- |
|    0-3 | Slewrate (ignored) |
|    4-7 | Gamma (ignored) |
|   8-11 | RGBW (ignored) |
|  12-13 | Channel |
|  14-17 | Device Id |

### Send Composite Actor (Smart Actors)

This package is send for smart actors only. It allows setting the speed of the fade in 100ms or 1s units (depending on bit 14 of 'Time'). Bit 15 is set to jump to 100% immediately.

| Offset | Name |
| -----: | :---------- |
|      0 | Send Actor Package (see above) |
|    8-9 | Time (0x0000-0x3FFF = time, bit 14:multiply time by 10, bit 15:100% jump flag) |
|  10-11 | unused |
