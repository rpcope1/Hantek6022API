Hantek6022API
=============

Hantek 6022BE Python API for Windows. This is a wrapper for Python via ctypes for Hantek's SDK for the ultra-cheap, reasonably usable
(and ultra-hackable) 6022BE DSO. I was tired of using the silly Chinese software that came with this DSO, so I decided
to write a wrapper so I could run the scope through Python. 

The scope can be accessed by instantiating an oscilloscope object with the correct scopeid (always 0 for one scope
attached). Things like voltage divisions and sampling rates can be set by the appropriate methods. As I finish developing
this, I will include documentation. Each method has some documentation as to what it does currently though, and hopefully
variable names are clear enough to give you some idea what they are for. Finally the unit tests at the end that are
run when calling the script directly also may shed some light on what things do.

If you have any requests for features, bugfixes, or comments, please let me know, and happy hacking.

(Also, the provided DLLs that access the scope belong to Hantek, not me. They are provided simply for ease of access and
are probably NOT covered by the GPL!)

Note to whomever may be using this:
I've noticed that while you have more control here, this sometimes runs a little slower than with the included scope program.
I need to figure how to speed up access. Part of the problem, I suspect, is crappy drivers, and crappy firmware (you get what
you pay for I guess). I am looking into hacking some drivers together, and maybe that will fix some of the functionality problems
like calibration not working, and provide a speed increase in the API.

As far as firmware goes, it looks as though the internal firmware is reasonably common. It may be feasible to rewrite this,
and get better performance/sampling speed increase? Also, the roughly +/-10mV noise on the scope (according to Aurora at eevblog.com) 
may be due to a DC/DC converter on the board. This might be work replacing if noise can be dropped by any significant factor.

For additional (interesting) details, the inquisitive reader is suggested to read:
http://www.eevblog.com/forum/testgear/hantek-6022be-20mhz-usb-dso/
