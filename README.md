# Inside Loxone Miniserver, Extensions and Devices

I talk about three different device types in this document:

  - Miniserver: the server hardware. At least one is required for a home.
  - Extensions: connected to the Miniserver via the Loxone Link bus.
  - Devices: connected to one of the two Tree Busses behind a Tree Extension or via IPv6 868MHz to an Air Base Extension.

I've split up the documentation into separate parts to make it easier to read, also because Legacy and NAT protocols are completely independent, you only need to care about the one that matters for you.

- Hardware
    - [Loxone Miniserver Hardware](LoxoneMiniserverHardware.md)
    - [Loxone Miniserver Go Hardware](LoxoneMiniserverGoHardware.md)
- Loxone Link Protocol
    - [Loxone Link Hardware](LoxoneLinkHardware.md)
    - [Loxone Link Protocol Introduction](LoxoneLinkProtocolIntro.md)
    - [Loxone Link Legacy Protocol](LoxoneLinkLegacyProtocol.md)
        - [Loxone Relay Extension](LoxoneLinkLegacyExtensionRelay.md)
        - [Loxone Extension](LoxoneLinkLegacyExtension.md)
    - [Loxone Link NAT Protocol](LoxoneLinkNATProtocol.md)
        - [Loxone Link Tree Extensions and Devices](LoxoneLinkNATTreeDevices.md)
