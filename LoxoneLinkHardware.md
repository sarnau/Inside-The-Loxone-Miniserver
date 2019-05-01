# CPUs in the Miniserver, Extensions and Devices

I will talk about four different device types in this document:

  1. Miniserver: It supports one Loxone Link bus and is the only device talking to the extensions on the bus.
  - Extensions: Connected to the Miniserver via the Loxone Link bus.
  - Tree Devices: Connected to one of the two Tree Busses behind a Tree Extension. Because of this, devices have their own NAT plus the Tree Base Extension NAT to be addressed by the Miniserver.
  - Air Devices: Connected using IPv6 868MHz via an Air Base Extension. Because of this, devices have their own NAT plus the Air Base Extension NAT to be addressed by the Miniserver.

## Loxone Extensions and Devices CPUs

There are four known CPUs used in Loxone Link devices. They are technically very similar, but because TI no longer recommends their Stellaris CPUs for new designs, Loxone switched to the ST32 architecture for newer designs. The only exception is the Miniserver, which uses an Atmel ARM CPU.

They all support reprogramming of their flash, which allows easy software updates without additional hardware. All extensions have a 2kb-8kb boot loader. The boot loader launches the code and also validates and installs a software update, if available.

- Atmel AT91SAM9G20 from Microchip
This one is only used by the Miniserver. It is a 400MHz ARM926 with 32kb internal SRAM and 64kb internal ROM. The server has two SD RAM chips (H57V2562GTR from SK Hynix) as additional memory with 256MBit each adding another 64MB of memory. The actual software is on an SD card, it is therefore not limited to the internal FLASH of the chip. It is loaded into the SD RAM by the boot loader. The serial number of the Miniserver is its Ethernet MAC address. The CPUs costs 7-8 €.

- Stellaris (LM3S2678) from TI
This is a 32-bit ARM Cortex M3 CPU with 128kb Flash and 32kb SRAM. It has a built-in CAN bus controller. While it can be clocked up to 50MHz, it seems to be only clocked at 8MHz. The CPUs costs around 6 €.

    Examples are:

    - Extension
    - Dimmer Extension
    - Relay Extension
    - RS232 Extension
    - RS485 Extension
    - Modbus Extension
    - EnOcean Extension
    - Fröling Extension
    - DMX Extension
    - 1-Wire Extension
    - IR Extension (not sure about this one, it clearly has a smaller boot loader - only 4kb, instead of 8kb)

    The memory layout is as follows:
    - `0x00000000-0x00001FFF` : boot loader (8kb, the IR Extension has only 4kb of boot loader)
    - `0x00002000-0x00011FFF` : firmware (contained in the `*.upd` files, the IR Extension has starts at 0x1000)
    - `0x00012000-0x00033FFF` : firmware update area
    - `0x20000000-0x20007FFF` : 32kb SRAM
    - `0x40000000-0x43FFFFFF` : Peripherals
    - `0xE0000000-0xE0040FFF` : ARM special area


- STM32F3 (STM32F302CCT6) from ST
This is a 32-bit ARM Cortex M4 CPU with 256kb Flash and 40kb SRAM. It also has a built-in CAN bus controller, which means an external MCP2515 is not required. While it can be clocked up to 72MHz, it is also only clocked at 8MHz (devices, DI Extension, AI Extension, AO Extension) or 64Mhz (the Tree Extension). The CPUs costs less than 2.5 €. The integrated CAN bus controller saves another 1.5 € (MCP2515 price), resulting in significant cost savings by using the STM32. I would guess that any of the small extensions cost less than 10 € in material.

    Examples are:
    
    - Dali Extension
    - Tree Extension
    - DI Extension
    - AI Extension
    - AO Extension
    - Internorm Extension
    - Dimmer Extension v2
    - All Tree devices

    The memory layout is as follows:
    - `0x08000000-0x080007FF` : boot loader (2kb)
    - `0x08000800-0x0803FFFF` : firmware (contained in the `*.upd` files)
    - `0x1FFFF800-0x1FFFD7FF` : Option bytes and System memory
    - `0x20000000-0x20009FFF` : 40kb SRAM
    - `0x40000000-0x500007FF` : Peripherals
    - `0xE0000000-0xFFFFFFFF` : ARM special area

- ZWIR4502 from ZMDI/IDT
The module is a secure low-power wireless IPv6 communication module supporting the 868/915 MHz frequency bands. It is based on the STM32 (specifically the STM32F103RC) and is a 32-bit ARM Cortex M3 CPU with 256kb Flash and 48kb SRAM. They are clocked at 8Mhz. <https://www.idt.com/products/interface-connectivity/ipv6-modules/zwir4512-secure-low-power-wireless-ipv6-module> It costs between 15-20 €, depending on the number of units.

    Examples are:
    
    - Air Base Extension
    - Loxone Miniserver Go, which contains the Air Base Extension
    - All Air devices

    The memory layout is as follows:
    - `0x08000000-0x08000FFF` : boot loader (4kb)
    - `0x08000800-0x0803FFFF` : firmware (contained in the `*.upd` files)
    - `0x1FFFF800-0x1FFFD7FF` : Option bytes and System memory
    - `0x20000000-0x2000BFFF` : 48kb SRAM
    - `0x40000000-0x500007FF` : Peripherals
    - `0xE0000000-0xFFFFFFFF` : ARM special area


## LED status of wired extensions or Tree devices

- blinking green: extension/device is working, communication with Miniserver is active - certain Tree devices, like the Tree Motionsensor, do not blink when everything is ok.
- blinking orange: extension/device is parked, communication with Miniserver is active
- blinking red: communication with Miniserver is not working, typically a wiring error on the bus
- blinking orange/red: update in process
- fast blinking red/green/orange: extension/device is identified/selected in Loxone Config
