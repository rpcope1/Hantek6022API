__author__ = 'Jochen Hoenicke'

from PyHT6022.LibUsbScope import Oscilloscope

scope = Oscilloscope()
scope.setup()
scope.open_handle()
eeprom = scope.read_eeprom(0, 256)
scope.close_handle()

print eeprom.encode('hex')
