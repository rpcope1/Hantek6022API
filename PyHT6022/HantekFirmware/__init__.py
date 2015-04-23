__author__ = 'Robert Cope'

from collections import namedtuple

# Firmwares to bootstrap the Hantek 6022BE Device are located in this module.
# Format: (Data Len, Value, Data) (Index is always 0x00).
FirmwareControlPacket = namedtuple('FirmwareControlPacket', ['size', 'value', 'data'])

from stock_firmware import stock_firmware
from mod_firmwares import mod_firmware_01

default_firmware = mod_firmware_01

