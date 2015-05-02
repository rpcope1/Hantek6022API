__author__ = 'Robert Cope'

from collections import namedtuple
import os
import array

# Firmwares to bootstrap the Hantek 6022BE Device are located in this module.
# Format: (Data Len, Value, Data) (Index is always 0x00).
FirmwareControlPacket = namedtuple('FirmwareControlPacket', ['size', 'value', 'data'])


def fx2_ihex_to_control_packets(firmware_location):
    packets = []
    # disable 8051
    packets.append(FirmwareControlPacket(1, 0x7f92, '\x01'))
    packets.append(FirmwareControlPacket(1, 0xe600, '\x01'))
    with open(firmware_location, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            assert line.startswith(":")
            record_len = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            record_type = int(line[7:9], 16)
            raw_data = line[9:-2]
            record_data = [int(raw_data[i:i+2], 16) for i in xrange(0, len(raw_data), 2)]
            file_checksum = int(line[-2:], 16)
            assert record_len == len(record_data)
            if record_type == 0x00:
                checksum = (sum(record_data) + record_len + (addr % 256) + (addr >> 8)) % 256
                assert not ((checksum + file_checksum) % 256) & 0xFF
                packets.append(FirmwareControlPacket(record_len, addr, array.array('B', record_data).tostring()))
            elif record_type == 0x01:
                assert file_checksum == 0xFF
                break;
            else:
                raise ValueError('Unknown record type 0x{:2x} encountered!'.format(record_type))
    # enable 8051
    packets.append(FirmwareControlPacket(1, 0x7f92, '\x00'))
    packets.append(FirmwareControlPacket(1, 0xe600, '\x00'))
    return packets

base_path = os.path.dirname(os.path.realpath(__file__))
stock_firmware = fx2_ihex_to_control_packets(os.path.join(base_path, 'stock', 'stock_fw.ihex'))
mod_firmware_01 = fx2_ihex_to_control_packets(os.path.join(base_path, 'modded', 'mod_fw_01.ihex'))
mod_firmware_iso = fx2_ihex_to_control_packets(os.path.join(base_path, 'modded', 'mod_fw_iso.ihex'))

default_firmware = mod_firmware_iso

