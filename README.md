# Inside Loxone Miniserver, Extensions and Devices

I talk about three different device types in this document:

  - Miniserver: the server hardware. At least one is required for a home.
  - Extensions: connected to the Miniserver via the Loxone Link bus.
  - Devices: connected to one of the two Tree Busses behind a Tree Extension or via IPv6 868MHz to an Air Base Extension.

I've split up the documentation into separate parts to make it easier to read, also because Legacy and NAT protocols are completely independent, you only need to care about the one that matters for you.

I am also providing a collection of Python scripts for the Miniserver, feel free to look into them, to see if they are helpful for you.

- Hardware
    - [Loxone Miniserver Hardware](LoxoneMiniserverHardware.md)
    - [Loxone Miniserver Go Hardware](LoxoneMiniserverGoHardware.md)
    - [Loxone Extensions and devices debug connectors](LoxoneDebugConnectors.md)
- Miniserver Firmware
    - [Loxone SD Card Hardware](LoxoneSDCards.md)
    - [Loxone SD Card Format](LoxoneSDCardFormat.md)
- Loxone Link Protocol
    - [Loxone Link Hardware](LoxoneLinkHardware.md)
    - [Loxone Link Protocol Introduction](LoxoneLinkProtocolIntro.md)
    - [Loxone Link Legacy Protocol](./Legacy/LoxoneLinkLegacyProtocol.md)
        - [Loxone Extension](./Legacy/LoxoneLinkLegacyExtension.md)
        - [Loxone Relay Extension](./Legacy/LoxoneLinkLegacyExtensionRelay.md)
        - [Loxone RS232 Extension](./Legacy/LoxoneLinkLegacyExtensionRS232.md)
        - [Loxone RS485 Extension](./Legacy/LoxoneLinkLegacyExtensionRS485.md)
        - [Loxone DMX Extension](./Legacy/LoxoneLinkLegacyExtensionDMX.md)
        - [Loxone 1-Wire Extension](./Legacy/LoxoneLinkLegacyExtension1Wire.md)
        - [Loxone Modbus Extension](./Legacy/LoxoneLinkLegacyExtensionModbus.md)
    - [Loxone Link NAT Protocol](./NAT/LoxoneLinkNATProtocol.md)
        - [Loxone DI Extension](./NAT/LoxoneLinkNATExtensionDI.md)
        - [Loxone AI Extension](./NAT/LoxoneLinkNATExtensionAI.md)
        - [Loxone AO Extension](./NAT/LoxoneLinkNATExtensionAO.md)
        - [Loxone Tree Extension](./NAT/LoxoneLinkNATTreeExtension.md)
        - [Loxone Touch Tree Device](./NAT/LoxoneLinkNATTreeTouch.md)
        - [Loxone Touch Pure Tree Device](./NAT/LoxoneLinkNATTreeTouchPure.md)
        - [Loxone Valve Acutator Tree Device](./NAT/LoxoneLinkNATTreeValveActuator.md)
        - [Loxone Damper Tree Device](./NAT/LoxoneLinkNATTreeDamper.md)
        - [Loxone LED Devices](./NAT/LoxoneLinkNATLED.md)
        - [Loxone RGBW 24V Dimmer](./NAT/LoxoneLinkNATTreeRGBW24VDimmer.md)
        - [Loxone Room Comfort Sensor](./NAT/LoxoneLinkNATTreeRoomComfortSensor.md)
        - [Loxone Alarm Siren](./NAT/LoxoneLinkNATTreeAlarmSiren.md)
        - [Loxone Leaf Tree](./NAT/LoxoneLinkNATTreeLeaf.md)
        - [Loxone Weather Station Tree](./NAT/LoxoneLinkNATTreeWeatherStation.md)
        - [Loxone Motion Sensor Tree](./NAT/LoxoneLinkNATTreeMotionSensor.md)
        - [Loxone LED Ceiling Light Tree](./NAT/LoxoneLinkNATTreeLEDCeilingLight.md)

## Code Examples

- `unpackLoxoneMiniserverFirmwareUpdate.py` - Uncompresses an `*.upd` firmware update, which contains the firmware for the Miniserver as well as an update for the Miniserver filesystem.
- `analyzeLoxoneExtensionUpdates.py` - Analyzes the firmware updates for Loxone extension and devices (Name, Type, Version, CPU, ROM-Usage, RAM-Usage)
- `loadLoxoneMiniserverStatistics.py` - Example on how to load the statistics from the Miniserver via FTP and parse the files for further processing.
- `loadMiniserverConfigurationFile.py` - Load the current configuration from the Miniserver and uncompress it, so it can be opened with a text editor. Also describes the load order of configurations.
- `LoxoneMonitorServer.py` - A Loxone Monitor Server proxy example to simulate the debugging options Loxone has on your server.
- `LoxoneWeather.py` - A Loxone Weather Service proxy, which uses Darksky instead. It supports CSV and XML replies and also tries to match the icons.
- `parseLoxoneSD.py` - Parse a ZIP compressed disk image of the Micro-SD card. This can be used to recover files from the SD card directly.
- `decompressMiniserverArchive.py` - Decompresses the `/commonv2.agz` and `/images.zip` into `./web/`. The Miniserver keeps these files compressed and only the webserver serves them uncompressed. There are more files in the `/web/` hierarchy, as can be seen with an FTP client:

    - `/data/LoxAPP3.json` - a simplified version of the configuration
    - `/data/weatheru.bin` - Recent weather data in 108 byte chunks, see in the network section under Weather Server
    - `/stats/index.html` - Dynamic webpage with the server statistics
    - `/stats/styles.css` - CSS for the statistics webpage
