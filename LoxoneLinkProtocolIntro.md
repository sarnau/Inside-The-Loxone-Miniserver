# Loxone Link and Loxone Tree protocol

Loxone Link (in the past also called the "LoxBUS") is using a standard CAN 2.0B bus, clocked at 125kHz (which allows up to 500m of cable length). The Miniserver has a build-in 120Ω resistor, so the Miniserver has to be at one end of the bus. It doesn't use automatic retransmission and uses a sample point of 68.75% (1-10-5 time quantum) with a prescaler of 4 (at 8MHz clock rate), I do not expect this to be critical.

The Loxone Tree Extension uses two additional CAN 2.0B busses (driven by two MCP2515 CAN controllers), but are clocked at 50kHz (which allows up to 1km of cable length) via a prescaler of 10. There is also a minimal change in the address of Tree devices vs. extensions, but the protocol is otherwise identical. The Tree Extension has to be at the end of the Tree busses as well.

Packages are always using the extended frame format, therefore the object identifier is 29-bit (`0x00000000…0x1FFFFFFF`). The data packages are always 8 bytes long. Only the data frame is used. Any CAN bus monitor hardware will work just fine with the Loxone Link bus and the Tree Bus as well.

The Loxone Link bus is a strict server-client bus. The Miniserver sends data to the extensions, the extensions send data to the bus. Extensions never talk to each other (with the obvious exception of device bridges, like the Tree Extension and the Air Base Extension – but even in this case: the bridge is almost 100% transparent between the device and the server). The Miniserver can either multicast to all extensions of a specific type (used in the update case) or to one extension via direct commands.

For the first years Loxone stored the serial number and extensions type in the CAN object identifier. This is now called the "legacy protocol". With more extensions arriving and also extensions with devices behind them, Loxone ran out of space and flexibility with that scheme. The newly introduced NAT protocol does not interfere with existing extensions, but required a server update for support. Besides the Miniserver having to able to deal with both protocols, they are completely different. An extension either implements the legacy protocol or the new one, never both. All Tree devices are always using the newer NAT protocol. The Air Base extension and other gateway extensions are still using the legacy protocol to forward packages to Miniserver. The Air devices are using a special container format for their packages.

The 8 byte package contains a single byte, which is either a command (in the legacy protocol) or a device NAT (in the NAT protocol) plus a 7 byte payload. The only exception of this rule is the firmware update case for legacy extension. There are also fragmented packages possible, which allow transmitting more than 7 bytes to/from a device. This is used to configure extensions and heavily by the Air Base Extension to send messages to Air devices.

Extensions can send data to the bus at any time to inform the server. This is important for sensors or keypads to report their updated status.

While Loxone doesn't do it, it is easily possible to have a device on the Loxone Link bus, which acts as several extensions at once.
