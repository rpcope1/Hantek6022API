__author__ = 'Robert Cope'

from unittest import TestCase

from PyHT6022.LibUsbScope import Oscilloscope
from PyHT6022.HantekFirmware import stock_firmware, mod_firmware_01


# TODO: Add more unit tests, add unit tests for changing number of active channels.


class BasicTests(TestCase):
    def test_find_device(self):
        print ("Testing finding device and flashing stock firmware.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        assert scope.close_handle()

    def test_flash_firmware(self):
        print ("Testing flashing multiple firmwares.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        assert scope.flash_firmware(mod_firmware_01)
        assert scope.flash_firmware(stock_firmware, supports_single_channel=False)
        assert scope.close_handle()

    def test_get_cal_values(self):
        print ("Testing getting calibration values.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        cal_values = scope.get_calibration_values()
        assert cal_values
        assert scope.close_handle()

    def test_read_data(self):
        print ("Testing reading data from the oscilloscope.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        ch1_data, _ = scope.read_data(data_size=0x400)
        print(ch1_data)
        assert ch1_data
        assert scope.close_handle()

    def test_read_many_sizes(self):
        print("Testing reading many different data sizes")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        data_size = 0x400
        for _ in range(11):
            print("DATA SIZE", data_size)
            ch1_data, ch2_data = scope.read_data(data_size=data_size, raw=True)
            print(len(ch1_data))
            print(len(ch2_data))
            assert ch1_data, ch2_data
            data_size <<= 1
        assert scope.close_handle()

    def test_set_sample_rate(self):
        print("Testing setting the sample rate.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        for rate_index in scope.SAMPLE_RATES.keys():
            scope.set_sample_rate(rate_index)
        assert scope.close_handle()

    def test_set_channel_voltage_range(self):
        print("Testing setting the voltage range.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        for vrange in scope.VOLTAGE_RANGES.keys():
            assert scope.set_ch1_voltage_range(vrange)
            assert scope.set_ch1_voltage_range(vrange)
        assert scope.close_handle()

    def test_data_scaling(self):
        print("Testing setting various scale facotrs and reading.")
        scale_factor = 0x01
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        assert scope.set_ch1_voltage_range(scale_factor)
        assert scope.set_sample_rate(27)
        ch1_data, _ = scope.read_data(0x100000)
        ch1_data = scope.scale_read_data(ch1_data, scale_factor)
        print("Max:", max(ch1_data), "(V), Min:", min(ch1_data), "(V)")
        assert ch1_data
        assert scope.close_handle()

    def test_set_num_channels(self):
        print("Testing setting the number of channels with modified firmware.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(mod_firmware_01)
        assert scope.set_num_channels(1)
        assert scope.set_num_channels(2)
        assert scope.set_num_channels(1)
        assert scope.close_handle()

    def test_set_one_channel_and_read(self):
        print("Testing setting one channel and reading it.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware(mod_firmware_01)
        assert scope.set_ch1_voltage_range(0xA)
        assert scope.set_sample_rate(0x10)
        assert scope.set_num_channels(1)
        ch1_data, ch2_data = scope.read_data(0x4000)
        assert ch1_data
        assert not ch2_data
        assert scope.close_handle()

    def test_read_firmware(self):
        print("Testing read_firmware method on scope.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        assert scope.read_firmware()
        assert scope.close_handle()

    def test_clear_fifo(self):
        print("Testing explicitly clearing the FIFO.")
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        assert scope.clear_fifo()
        assert scope.close_handle()