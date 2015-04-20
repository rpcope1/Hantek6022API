__author__ = 'Robert Cope'

from unittest import TestCase

from PyHT6022.LibUsbScope import Oscilloscope


class BasicTests(TestCase):
    def test_find_device(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.close_handle()

    def test_flash_firmware(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.flash_firmware()
        assert scope.close_handle()

    def test_get_cal_values(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        cal_values = scope.get_calibration_values()
        assert cal_values
        assert scope.close_handle()

    def test_read_data(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        ch1_data, _ = scope.read_data(data_size=0x400)
        print ch1_data
        assert ch1_data
        assert scope.close_handle()

    def test_read_many_sizes(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
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
        for rate_index in scope.SAMPLE_RATES.keys():
            scope.set_sample_rate(rate_index)
        assert scope.close_handle()

    def test_set_channel_voltage_range(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        for vrange in scope.VOLTAGE_RANGES.keys():
            assert scope.set_ch1_voltage_range(vrange)
            assert scope.set_ch1_voltage_range(vrange)
        assert scope.close_handle()

    def test_data_scaling(self):
        scale_factor = 0x01
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        assert scope.set_ch1_voltage_range(scale_factor)
        assert scope.set_sample_rate(27)
        ch1_data, _ = scope.read_data(0x100000)
        ch1_data = scope.scale_read_data(ch1_data, scale_factor)
        print "Max:", max(ch1_data), "(V), Min:", min(ch1_data), "(V)"
        assert ch1_data
        assert scope.close_handle()