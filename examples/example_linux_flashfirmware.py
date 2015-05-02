__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope

scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.flash_firmware_from_hex('../PyHT6022/HantekFirmware/custom/build/firmware.ihx')
scope.close_handle()
