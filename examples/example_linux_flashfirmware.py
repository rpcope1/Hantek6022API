__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope

scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.flash_firmware()
scope.close_handle()