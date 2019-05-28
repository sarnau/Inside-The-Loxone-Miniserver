# Inside the Loxone Miniserver
 
I'd like to explain some technical details of the Loxone Miniserver and the Loxone Miniserver Go. The Miniserver (as well as all extensions) are ARM based, just like all modern mobile phones. It is clocked at just 8MHz.

The Miniserver is ARM based. The CPU is booting from a 512kb flash memory. This code then loads the actual operating system from the SD Card into the additional 64MB of memory and executes it from there.

## Hardware id

There are several different versions of Miniserver hardware:

- ` 40000` - first known version
- ` 60000` - KNX and Ethernet changes with different reset support
- ` 80000` - unknown changes
- ` a0000` - some SD card change, new Ethernet chip, [KSZ8081RNB][4b]
- ` c0000` - 128MB of SRAM (twice the amount of older versions)
- `100000` - Miniserver Go (based on the `a0000` Miniserver)


## CPU, Flash Memory, SRAM

The CPU is an Atmel [AT91SAM9G20][1] from Microchip. It is a 3,3V 400MHz ARM926 with 32kb internal SRAM and 64kb internal ROM. It is paired with a serial interface Flash memory ([AT25DF041A][2] from Adesto Technologies), which is updatable by Loxone – it is one of two chips mounted on the back of the board. This flash memory also contains non-volatile memory used by the Miniserver, like encryption keys, which are not stored on the SD card. The other important chips are two SD RAM chips ([H57V2562GTR][3] from SK Hynix) as additional memory with 256MBit each adding another 64MB of memory.

## Function of the AT25 FLASH memory

The FLASH memory contains the boot firmware for the CPU, which reads the Miniserver firmware from the MicroSD card into the RAM and launches it.

And while it is 512kb large it only uses about 12kb of its capacity. 10.25kb are reserved for the boot loader, followed by 256 bytes for an XML file with the hardware serial numbers and a 1.5kb area with the private encryption key.

The XML contains the SSDP `modelNumber` as the `Type`; the UUID, also used for SSDP; the MAC or serial number of the Miniserver and the production date.

    <?xml version="1.0" encoding="utf-8"?>
    <Serial Version="10">
        <Type>1</Type>
        <UUID>aabbccdd-eeff-0011-2233-445566778899</UUID>
        <MAC>50:4F:11:22:33:44</MAC>
        <Date>01.01.2018 01:23:45</Date>
    </Serial>


## Ethernet

The Ethernet is connected with another Chip from Microchip, the [KSZ8051RNL][4a] or [KSZ8081RNB][4b]. Which is a 10BASE-T/100BASE-TX Automotive Physical Layer Transceiver. It doesn't offer a lot, so most of the load for the different protocols TCP/IP and UDP, ARP, DHCP, etc. are all handled by the CPU.

## SD Card

The SD Card is accessed with some logic gates directly. Nothing special here.

## RTC Clock

The Miniserver has a battery backed CMOS Real-Time Clock (RTC) via a [PCF2123][5] from NXP Semiconductors. This allows the system to run without an internet connection, while still having a valid time. During boot it is set if possible by testing various NTP servers.

## Relays / Digital Out

The Relays are [HF33024-HLT][6], which are isolated from the CPU by two [ADuM3401][7] from Analog Devices.

## Analog Out

The Analog Out are driven by a [AD5724][8] also from Analog Devices, which is a a complete, quad, 12-/14-/16-Bit, serial input, unipolar/bipolar voltage output DAC. They are driven to have a 10V output range with a 12-bit resolution.

## Analog In

The Analog Ins are driving by a [TV1544][9] from Texas Instruments. It is a CMOS 10-bit switched-capacitor successive-approximation (SAR) analog-to-digital (A/D) converter.

## Digital In

The digital inputs are read by a [HVS882][10] from Texas Instruments. It is an 8-channel digital input serializer, which can handle up to 34V at the inputs with a flexible current limiter – it therefore also protects the CPU from damage. This is the other chip, which is mounted on the back of the board.

## Loxone Link

The Loxone Link bus is standard [CAN bus][11] connected via a CAN controller ([MCP2515][12], also Microchip) to the CPU. It is using a standard CAN Transceiver ([SN65HVD232D][13] from Texas Instruments) to protected the Miniserver from defects on the bus. The Miniserver also has a 120Ω resistor built-in, so it has to be on the end of the CAN bus. The CAN bus is clocked at 125kHz (which allows up to 500m of cable length for the Loxone Link bus).

All packages are using the extended frame format. The identifier is therefore always 29-bit (0…0x1FFFFFFF) and the data package is always 8 bytes long. Any CAN bus monitor hardware will work just fine with the Loxone Link bus.

The Loxone Link bus is a strict Master-Slave bus. The Miniserver as the master talks to the extensions, the extensions send data to the Miniserver. Extensions never talk to each other. The Miniserver can either multicast to all extensions or to specific extensions via direct commands. In the update case, it can send the update to all extensions of a certain type at the same time.

## Photo with Labels of the Mainboard

![Loxone Miniserver Mainboard](./img/LoxoneMiniserver.jpg)

 [1]: https://www.microchip.com/wwwproducts/en/AT91SAM9G20
 [2]: https://www.adestotech.com/wp-content/uploads/doc3668.pdf
 [3]: https://www.skhynix.com/eolproducts.view.do?pronm=SDR+SDRAM&srnm=H57V2562GTR&rk=01&rc=consumer
 [4a]: http://ww1.microchip.com/downloads/en/devicedoc/00002310a.pdf
 [4b]: http://ww1.microchip.com/downloads/en/devicedoc/ksz8081mnx-rnb.pdf
 [5]: https://www.nxp.com/docs/en/data-sheet/PCF2123.pdf
 [6]: http://www.hongfa.com/pro/pdf/HF33F_en.pdf
 [7]: http://www.analog.com/media/en/technical-documentation/data-sheets/ADUM3400_3401_3402.pdf
 [8]: http://www.analog.com/media/en/technical-documentation/data-sheets/AD5724_5734_5754.pdf
 [9]: http://www.ti.com/lit/ds/slas139c/slas139c.pdf
 [10]: http://www.ti.com/lit/ds/symlink/sn65hvs882.pdf
 [11]: https://de.wikipedia.org/wiki/Controller_Area_Network
 [12]: http://ww1.microchip.com/downloads/en/DeviceDoc/21801d.pdf
 [13]: http://www.ti.com/lit/ds/symlink/sn65hvd230.pdf
