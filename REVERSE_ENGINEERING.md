# Reverse Engineering this Oscilloscope

One of the more unfortunate things about this scope as it comes stock is that there is no support for Linux, and
the drivers, while they have an SDK, are essentially binary blobs. We think that we can do better, and the goal
is thus to be able to write an open source driver that can be used on Linux (or BSD, Mac OS X, or Windows, if you're
into that) to get more functionality out of this device. 

I am reverse engineering this scope by using the Windows SDK in a Windows VM, and watching USB traces on my Linux
host machine. From [jhoenicke](https://github.com/jhoenicke), I have confirmed that the following USB URB control 
commands map as follows:

| *Oscilloscope Command* | *bRequest Value* | *Other Notes*                                       |
|------------------------|------------------|-----------------------------------------------------|
|   Set CH0 voltage range|      0xE0        | Possible values: 1,2,5,10 (5V, 2.5V, 1V, 500mV).    |
|   Set CH1 voltage range|      0xE1        | Possible values: 1,2,5,10 (5V, 2.5V, 1V, 500mV).    |

|   Set Sampling Rate    |      0xE2        | Possible values: 48, 30, 24, 16, 8, 4, 1 (MHz) and 50,20,10 (*10kHz). |
|   Trigger Oscilloscope |      0xE3        | Host requests bulk data for scope trace after this. |



# Pull Requests/Issues

If you have any extra information about this scope, open a pull request or issue and share your knowledge! I am very
open to any ideas or input from anyone interested.