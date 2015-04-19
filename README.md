Hantek6022API
=============

Hantek 6022BE Python API for Windows. This is a wrapper for Python via ctypes for Hantek's SDK for the ultra-cheap, 
reasonably usable (and ultra-hackable) 6022BE DSO. I was tired of using the silly Chinese software 
that came with this DSO, so I decided to write a wrapper so I could run the scope through Python. 

The scope can be accessed by instantiating an oscilloscope object with the correct scopeid (always 0 for one scope
attached). Things like voltage divisions and sampling rates can be set by the appropriate methods. As I finish developing
this, I will include documentation. Each method has some documentation as to what it does currently though, and hopefully
variable names are clear enough to give you some idea what they are for. Finally the unit tests at the end that are
run when calling the script directly also may shed some light on what things do.

(Also, the provided DLLs that access the scope belong to Hantek, not me. They are provided simply for ease of access and
are probably NOT covered by the GPL!)

## TODO

 1. Clean up library, apply good formatting.
 2. Build *real* unit tests.
 3. Add a few examples.
 4. Look into adding compatibility to Linux (this will probably mean reverse engineering Windows USB drivers).

One excellent ultimate goal for this would to make it play nice with cheap ARM SBCs like the Raspberry Pi, such that
this could be used as a quick and dirty DAQ for many interesting systems.


For additional (interesting) details, the inquisitive reader should read:
http://www.eevblog.com/forum/testgear/hantek-6022be-20mhz-usb-dso/ 

UPDATE: If you're interested in contributing and updating this repo, I'd be glad to have help maintaining it.
 I do accept pull requests.
