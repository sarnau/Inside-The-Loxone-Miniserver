# Loxone Extensions and devices debug connectors

## LM3S2678 (64-Pin LQFP) (Legacy extensions)

This CPU was used in all legacy extensions. Many boards seem to share identical boards, just with minimal component changes, e.g. the 1-Wire and DMX extensions are identical. I assume that the RS232 and RS485 extension are similar, considering that the print on the board shows "Rx/Tx" and "B/A", which would match RS232 and RS485.


### Board Layout

    24V +                           GND O O GND
    24V -                                O  Antenna
                                    GND O O GND
                    7 5 3 1
    Link +          O O O O              O DQ  (Rx/B/1W)
    Link -          O O O O              O GND 
                    8 6 4 2              O VDD (Tx/A/5V)


### JTAG/SWD

For this CPU JTAG and SWD are available on the connector.

| Pin | LM3S2678 Pin       |
| :-: | :----------------- |
|  1  | 28 (VDD, 3.3V)     |
|  2  | 49 (PC3/TDO/SWO)   |
|  3  | 29 (GND)           |
|  4  | 52 (PC0/TCK/SWCLK) |
|  5  | 29 (GND)           |
|  6  | 51 (PC1/TMS/SWDIO) |
|  7  | 40 (/RST)          |
|  8  | 50 (PC2/TDI)       |


## STM32F302CCT6 (48-Pin LQFP) (newer extensions and all Tree devices)

This CPU is used for the Tree Extension, but also all Tree devices. In this example I look at the Tree Extension board **only**.


### Board Layout

    24V +         O O O O O O            O White
    24V -         1 2 3 4 5 6                 
                                         O Green

    Link +                               O White
    Link -                        
              O O O                      O Green
              9 8 7

### JTAG/SWD

For this CPU only SWD is available on the connector.

PA9/PA10 are possibly used during development, allowing them conveniently to be tied to GND, which is available between them.

| Pin | STM32F3 Pin       |
| :-: | :----------------- |
|  1  | 48 (VDD, 3.3V) |
|  2  | 37 (PA14/SWCLK-JTCK) |
|  3  | 35 VSS/GND |
|  4  | 34 (PA13/SWDIO-JTMS) |
|  5  | 7 (NRST) |
|  6  | 44 (BOOT0) |
|  7  | 30 (PA9) |
|  8  | 35 VSS/GND |
|  9  | 31 (PA10) |

## ZWIR4512AC2 (Loxone Air)

I am looking at the Loxone Air Door/Windowcontact here as an example:

### Board Layout (front)

    O GND                O--------O





                         d c b a
    O GND                O O O O
    

### Board Layout (back)

    O GND          O
                            O O O O O O
                            6 5 4 3 2 1 
                     O
                     O
                     O
                     
                            O  O
                                
    O GND                O--------O
    
### SWD

For this CPU only SWD is available on the connector. The connector pins 1-6 are identical to the STM32F3 connector, but the connector has to be flipped by 180 degrees. This CPU type is very rare, but it is quite similar to the STM32F302CCT6, which works for SWO debugging.

| Pin |     | ZWIR4512AC2 Pin       |
| :-: | :-: | :----------------- |
|  1  |  a  | VCC |
|  2  |     | 24 TCK (PA14, JTAG – TCK, SWCLK) |
|  3  |  c  | GND |
|  4  |     | 22 TMS (PA13, JTAG – TMS, SWDIO) |
|  5  |  b  | 11 /RESET (NRST) |
|  6  |  d  | 16 BSEL (BOOT0) |

Other used pins on the ZWIR4512AC2 CPU:

| Pin | Name           | Function |
| :-: | :------------- |:------- |
|  8  | GPIO0/PA0/WKUP | reed contact |
|  9  | GPIO12/PC13    | button |
| 19  | GPIO10/PA11    | LED red |
| 20  | GPIO11/PA12    | LED green |
