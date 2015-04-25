# Reverse Engineering this Oscilloscope

One of the more unfortunate things about this scope as it comes stock is that there is no support for Linux, and
the drivers, while they have an SDK, are essentially binary blobs. We think that we can do better, and the goal
is thus to be able to write an open source driver that can be used on Linux (or BSD, Mac OS X, or Windows, if you're
into that) to get more functionality out of this device. 

I am reverse engineering this scope by using the Windows SDK in a Windows VM, and watching USB traces on my Linux
host machine. From [jhoenicke](https://github.com/jhoenicke), I have confirmed that the following USB URB control 
commands map as follows:

| *Oscilloscope Command* | *bRequest Value* | *Other Notes*                                                          |
|------------------------|------------------|------------------------------------------------------------------------|
|   Set CH0 voltage range|      0xE0        | Possible values: 1,2,5,10 (5V, 2.5V, 1V, 500mV).                       |
|   Set CH1 voltage range|      0xE1        | Possible values: 1,2,5,10 (5V, 2.5V, 1V, 500mV).                       |
|   Set Sampling Rate    |      0xE2        | Possible values: 48, 30, 24, 16, 8, 4, 1 (MHz) and 50,20,10 (*10kHz).  |
|   Trigger Oscilloscope |      0xE3        | Clear the FIFO on the FX2LP                                            |
|   Read/Write EEPROM    |      0xA2        | Read or write the eeprom built into the scope.                         |
|   Read/Write Firmware  |      0xA0        | Read or write the scope firmware. Must be done on scope initialization |

All commands are sent with index = 0x00, the calibration commands are sent with value 0x08, the 0xEx requests are sent
with value 0x00, and the value for R/W command is dependent on the Cypress protocol for interacting with the firmware.

Additionally, a bulk read from end point 0x86 reads the current contents of the FIFO, which the ADC is filling. The
reference Python libusb code should give further insight into the means for which to interact with the device.

# EEPROM

The device contains a 512 byte eeprom.  The first 8 byte of the eeprom
are important for startup.  They contain the initial USB vendor and
device id to allow it to be detected before the firmware is flashed.
See chapter 3.4.2 of the ez-usb technical reference manual.

The next 32 bytes are used by the windows SDK to store calibration data.  They
have no effect to the device itself.

# Modified and stock firmware

Because the IC that controls the device in the Hantek 6022BE, a Cypress CY7C68013A (FX2LP), uses an embedded 8051, and
firmware is flashed on device connection, it is possible to used modified firmware instead of the stock firmware in
order to get better performance from the device.

By default the Python reference library will load modified firmware into the device, written by 
[jhoenicke](https://github.com/jhoenicke), to extract more performance out of the device. The stock Hantek firmware
is provided so that it may be flashed an utilized as well.

# Pull Requests/Issues

If you have any extra information about this scope, open a pull request or issue and share your knowledge! I am very
open to any ideas or input from anyone interested.
