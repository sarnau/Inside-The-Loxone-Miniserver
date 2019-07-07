# Loxone MicroSD Cards

Loxone states the following on their website:

> Use only Loxone SD cards for the Miniserver. All SD cards have their own CPU which manages the flash memory. For optimum performance, Loxone OS accesses many low-level functions of the SD card, unlike, for example, a digital camera.

Wow, this is exciting! What mystery low level functions are they using? Time to find out.

The server ships with a 4GB Micro SD Card, which is of the SDHC type.

SD cards exists in many different varieties, but have to follow the specifications from the SD Group. This includes the communication on the bit level, as well as how commands are executed. However, there are options to have custom commands or at least non-mandatory commands. It is also possible to only support a subset of commands for a manufacturer, if they supply specific SD cards. Loxone could do that, but it is not probable, just because it makes it really hard for them to switch vendors for their SD cards, if prices and or availability changes. You don’t want to release an update to the Miniserver for different types of SD cards.

As I already looked at the mainboard of the Miniserver, it seems the CPU is talking directly to the SD card. That is not a surprise, considering that even Arduinos can do that easily. The Miniserver does that with the help of some gate logic, probably for buffering. I didn’t really care to look into the exact implementation details too much here.

Considering that the physical communication is standardized and that the actual firmware is read from the SD card by the boot code from the flash memory, I don’t expect too much special code for reading. And I am correct: the initialization phase for the SD card seems to follow the specification from the SD Group perfectly and can detect all types of SD cards up to SDHC.

The detailed information collected during initialization about the card can be requested from Loxone Config via “Detailed Device Info”:

> SD-Test: SD performance read=403kB/s write=345kB/s no error (0 0), ManufactorerID 2 Date 2016/3 CardType 2 Blocksize 512 Erase 0 MaxtransferRate 25000000 RWfactor 2 ReadSpeed 22222222Hz WriteSpeed 22222222Hz MaxReadCurrentVDDmin 3 MaxReadCurrentVDDmax 5 MaxWriteCurrentVDDmin 5 MaxWriteCurrentVDDmax 1 Usage:1.71%

What does these things mean?

- `read` = measured data read performance in kB/s after 1MB of reading a test file
- `write` = measured data write performance in kB/s after 1MB of writing a test file
- `no error` (0 0) = number of errors with this SD card (first number/error code = 0: no error, 1: read error, 2: verify error, second number: number of errors)
- `ManufactorerID` (yes, that is probably an original Austrian typo) = The manufacturer of the card. The ID is assigned by the SD Group.
- `Date` = Manufacturing date of the card
- `CardType` = 0 = unknown, 1 = SDv2, 2 = SDHC, 3 = SDv1 - detected during initialization
- `Blocksize` = 512 bytes (I think it this is true for all cards)
- `Erase` = `DATA_STAT_AFTER_ERASE` from the SCR register. Defines the data status after erase.
- `MaxtransferRate` = TRAN_SPEED` `from the CSD register. Maximum data transfer rate per one data line in bit/s
- `RWfactor` = `R2W_FACTOR` from CSD register (0 = 1, 1 = 2 (write half as fast as read) , 2 = 4, 3 = 8, 4 = 16, 5 = 32)
- `ReadSpeed` = 133333333 / (2 * ((133333333 / (2 * `MaxtransferRate`)) + 1))
- `WriteSpeed` = 133333333 / (2 * ((133333333 / (2 * `MaxtransferRate`)) + 1)) (always identical to ReadSpeed)
- `MaxReadCurrentVDDmin` = `VDD_R_CURR_MIN` from CSD register (0=0.5mA; 1=1mA; 2=5mA; 3=10mA; 4=25mA; 5=35mA; 6=60mA; 7=100mA)
- `MaxReadCurrentVDDmax` = `VDD_R_CURR_MAX` from CSD register (0=1mA; 1=5mA; 2=10mA; 3=25mA; 4=35mA; 5=45mA; 6=80mA; 7=200mA)
- `MaxWriteCurrentVDDmin` = `VDD_W_CURR_MIN` from CSD register (0=0.5mA; 1=1mA; 2=5mA; 3=10mA; 4=25mA; 5=35mA; 6=60mA; 7=100mA)
- `MaxWriteCurrentVDDmax` = `VDD_W_CURR_MAX` from CSD register (0=1mA; 1=5mA; 2=10mA; 3=25mA; 4=35mA; 5=45mA; 6=80mA; 7=200mA)
- `Usage` = How much of the SD card is used by data

 
The maximum supported capacity is 16GB, so do not use larger ones.

All the technical information is reported from the SD card and only for information. After initialization, what else does the Miniserver do to communicate to the card?

- Reading blocks via Block Read (`CMD17`)
- Writing blocks via Block Write (`CMD18`)
- Erasing blocks by simply writing empty blocks
- Repair after errors: power cycle the SD card and reinitialize the card (just as when the server is booting)

There are three different types of SD Card errors possible:

- Hardware errors during reading/writing. They occur within the low-level communication with the SD card itself. In this case a repair is automatically tried.
- CRC error. The Loxone filesystem has checksums over each block. If they don't match, it is an error – this could potentially happen, if the SD card is defect. But the software also tries to do a repair.
- SD card is full. The Miniserver tries to write data, but there is no more space on the SD card.

The Miniserver <em>only</em> uses mandatory commands, this means every single SD card in the market has to implement them. Therefore any SD card from any good manufacturer should work just fine in the Miniserver. That said: there are Chinese manufacturers who sell SD cards with a limited actual capacity (e.g. 2GB) but which identify themselves as e.g. 16GB cards. This will result in data loss!
