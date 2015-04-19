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
|   Trigger Oscilloscope |      0xE3        | Host requests bulk data for scope trace after this. |



# Pull Requests/Issues

If you have any extra information about this scope, open a pull request or issue and share your knowledge! I am very
open to any ideas or input from anyone interested.