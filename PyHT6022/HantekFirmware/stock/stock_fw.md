This file describes the most important functions and variables
in the stock firmware.

# firmware blocks

| *start* | *end* | *Info                                          |
|------|------|----------------------------------------------------|
| 095e | 0960 |  patch: set bit 5 (highspeed) |
| 0cb8 | 0d52 | init (called by main) |
| 0b7b | 0bdd | FIFO RESET (handle e4 packet) |
| 0028 | 002a |  Vector?? |  
| 0040 | 0042 |  Vector?? |  
| 0046 | 0048 |  Vector?? |  
| 104c | 1089 | set config | 
| 12dd | 12ef | get config |
| 1301 | 1309 | set interface |
| 12ef | 1301 | get interface | 
| 0048 | 004a | get status helper (noop) |
| 004e | 0050 | get status helper2 (noop) |
| 0050 | 0002 | get status helper3 (noop) |
| 0056 | 04d9 | Handle custom control packet (a2, b2, e0-e8)   |
| 1281 | 1299 | SUDAV (Setup Data Available) handler |
| 12b1 | 12c7 | SUTOK (Setup Token Received) handler |
| 12c7 | 12dd | SOF (Start of Frame) handler |
| 1089 | 10c0 | USB RESET (Bus Reset) handler |
| 1299 | 12b1 | SUSPEND (USB Suspend request) handler |
| 10c0 | 10f7 | HISPEED (Entered high-speed operation) handler |
| 002a | 002b | usb18 (reti) |
| 0032 | 0033 | usb1c (reti) |
| 0042 | 0043 | usb20 (reti) |
| 004a | 004b | usb24 (reti) |
| 0052 | 0053 | usb28 (reti) |
| 0bf9 | 0c00 | usb2c-usb48 (reti) |
| 0dfa | 0e00 | usb4c-usb60 (reti) |
| 1311 | 1323 | usb61-usbb4 (reti) |
| 0f73 | 0fbd | write eeprom | 
| 112d | 1162 | eeprom write packet handler |
| 0fbd | 1006 | read eeprom  |
| 0960 | 0a72 | patch: waveform data, gpif shadow register to e000 |
| 0f18 | 0f73 | setup GPIF registers and wave form (called from init) |
| 0036 | 0040 | 0 1 2 2 3 3 4 4 5 5 |
| 0773 | 095e | main |
| 04d9 | 0773 | handle packet (called by main after SUDAV interrupt) |
| 0033 | 0036 | WAKEUP/WU2Pin or USB Resume Vector | 
| 002e | 0032 | WAKEUP ISR |
| 002b | 002e | Timer2 Vector |
| 1196 | 11c8 | Timer2 ISR |
| 0e00 | 0e92 | USB descriptor data |
| 1229 | 1255 | wakeup part 1?? |
| 0003 | 0017 | INT0# Pin Vector (IE0) |
| 11fa | 1229 | setup USB (RENUM) |
| 1309 | 1311 | reset i2c state |
| 10f7 | 112d | wait for i2c ack |
| 11c8 | 11fa | setup i2c for writing |
| 1162 | 1196 | setup i2c for reading |
| 004b | 004e | Vector |
| 0a73 | 0b7b | I2C interrupt handler |
| 1255 | 1281 | lookup string in table (usb GET DESCRIPTOR STRING) |
| 0bdd | 0bf9 | read from i2c |
| 0dde | 0dfa | write to i2c |
| 1006 | 104c | delay (time in ms?) |
| 0017 | 0028 | delay 3000 cycles |
| 0043 | 0046 | USB Vector |
| 0053 | 0056 | GPIF/FIFO/Int4 Vector |
| 0c00 | 0cb8 | USB/GPIF interrupt table |
| 0000 | 0003 | Reset Vector: Jumps to startup
| 0d52 | 0d5e | Program Entry part 1|
| 0e92 | 0ebf | Read byte from memory (internal/external/code)|
| 0ebf | 0ee1 | Write byte to memory (internal/external/code)|
| 0ee1 | 0ef2 | compare two 32 bit numbers |
| 0ef2 | 0f18 | get address from table switch |
| 0d5e | 0dde | Program Entry part 2; patch the patch data|
| 0a72 | 0a73 | patch data end |


# variables

| *addr*|  *Info*                                         |
|-------|-------------------------------------------------|
| 08/09 | led blink timer                                 |
| 0a/0b | usb config descriptor highspeed mode            |
| 0c/0d | usb device descriptor                           |
| 0e/0f | usb config descriptor                           |
| 10/11 | usb config descriptor other speed mode          |
| 12/13 | usb config descriptor fullspeed mode            |
| 14/15 | usb device qualifier                            |
| 16/17 | usb string table                                |
| 18    | usb interface                                   |
| 19    | i2c id of eeprom (0x50 or 0x51)                 |
| 1a    | use second waveform (high speed sampling)       |
| 1b    | usb config                                      |
| 1c    | 16 bit eeprom present?                          |
| 1d    | e4 packet sent (=1) / acknowledges (=2)         |
| 35    | control packet - first data byte                |
| 36-3b | eeprom pointers                                 |
| 3c    | i2c packet len                                  |
| 3d    | i2c memory (external/internal)                  |
| 3e/3f | i2c memory address                              |
| 40    | i2c memory current offset                       |
| 41    | i2c state                                       |

bits:


| *bit* |  *Info*                                         |
|-------|-------------------------------------------------|
| 1h    | setup data pending                              |
| 2h    | green led signalling                            |
| 3h    |                                                 |
| 4h    | suspend pending                                 |
| 5h    | high speed                                      |
| 6h    | usb renum flag???                               |



# USB descriptors

The USB descriptors are at offset `0x0e00` in the firmware.  There are
some curiosities:

- Vendor of uninitialized device is `0x04b4` (Cypress Semiconductor Corp.)
  who is the designer of the ez-usb chip.
- Vendor of initialized device is `0x04b5` (ROHM LSI Systems USA)
  who is probably not related to this device at all.
- The device configures two endpoints: 2 (output), 6 (input).  Endpoint 2
  is never used, but prevents endpoint 6 to take the full 4kb fifo.
- The low speed configuration claims 4 endpoints, but defines only 2.
- The manufacturer string is `OEM   ` (with three spaces).
  The product string is `HantekDSO6022BE `.
