__author__ = 'Robert Cope'

from collections import namedtuple
from stock_firmware import stock_firmware
from mod_firmwares import mod_firmware_1

# Firmwares to bootstrap the Hantek 6022BE Device are located here.
# Format: (Data Len, Value, Data) (Index is always 0x00).

FirmwareControlPacket = namedtuple('FirmwareControlPacket', ['size', 'value', 'data'])
device_firmware = [FirmwareControlPacket(packet[0],
                                         packet[1],
                                         "".join(map(chr, packet[2]))) for packet in mod_firmware_1]

