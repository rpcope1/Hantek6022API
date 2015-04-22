__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope

scope = Oscilloscope()
scope.setup()
scope.open_handle()
firmware = scope.read_firmware()
scope.close_handle()

print firmware
