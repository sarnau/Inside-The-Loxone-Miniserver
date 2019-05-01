# Relay Extension (`0x0B`)

This extension is the most basic one, it is a simpler version of the [Loxone Extension](LoxoneLinkLegacyExtension.md).

| Command | Phase    | Dir | B0 | val16 | val32 | Description |
| ------- | -------- | --- | -- | ----- | ----- | ----------- |
|  0x60   |          | S↔E |    |       |       | Set or return the status of the 14 output relays. |
|  0x53   | Idle     | S←E | XX | YYYY | temperature | Overheating warning from an extension, as described in the Overheating protection section in the documentation for the Link Legacy format. |

If the Miniserver sets the output relays, the extension returns the actual state back to the Miniserver. If the overheating protection is active, all relays will be turned off and the extension returns 0 for their states. The extension doesn't returns its status _only_ after receiving a `0x60` command!