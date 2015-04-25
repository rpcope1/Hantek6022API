__author__ = 'Robert Cope'

from unittest import TestCase

from PyHT6022.LibUsbScope import Oscilloscope
from PyHT6022.HantekFirmware import stock_firmware, mod_firmware_01


# TODO: Add more unit tests, add unit tests for changing number of active channels.


class BasicTests(TestCase):
    def test_find_device(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        assert scope.close_handle()

    def test_flash_firmware(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        assert scope.flash_firmware(mod_firmware_01)
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        assert scope.close_handle()

    def test_get_cal_values(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        cal_values = scope.get_calibration_values()
        assert cal_values
        assert scope.close_handle()

    def test_read_data(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        ch1_data, _ = scope.read_data(data_size=0x400)
        print ch1_data
        assert ch1_data
        assert scope.close_handle()

    def test_read_many_sizes(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        data_size = 0x400
        for _ in xrange(11):
            print "DATA SIZE", data_size
            ch1_data, ch2_data = scope.read_data(data_size=data_size, raw=True)
            print len(ch1_data)
            print len(ch2_data)
            assert ch1_data, ch2_data
            data_size <<= 1
        assert scope.close_handle()

    def test_set_sample_rate(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        for rate_index in scope.SAMPLE_RATES.keys():
            scope.set_sample_rate(rate_index)
        assert scope.close_handle()

    def test_set_channel_voltage_range(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        for vrange in scope.VOLTAGE_RANGES.keys():
            assert scope.set_ch1_voltage_range(vrange)
            assert scope.set_ch1_voltage_range(vrange)
        assert scope.close_handle()

    def test_data_scaling(self):
        scale_factor = 0x01
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        assert scope.set_ch1_voltage_range(scale_factor)
        assert scope.set_sample_rate(27)
        ch1_data, _ = scope.read_data(0x100000)
        ch1_data = scope.scale_read_data(ch1_data, scale_factor)
        print "Max:", max(ch1_data), "(V), Min:", min(ch1_data), "(V)"
        assert ch1_data
        assert scope.close_handle()

    def test_set_num_channels(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(mod_firmware_01)
        assert scope.set_num_channels(1)
        assert scope.set_num_channels(2)
        assert scope.set_num_channels(1)
        assert scope.close_handle()

    def test_set_one_channel_and_read(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(mod_firmware_01)
        assert scope.set_ch1_voltage_range(0xA)
        assert scope.set_sample_rate(0x10)
        assert scope.set_num_channels(1)
        ch1_data, _ = scope.read_data(0x4000)
        assert ch1_data
        assert scope.close_handle()