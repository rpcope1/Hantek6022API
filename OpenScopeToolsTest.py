__author__ = 'Robert Cope'

from unittest import TestCase
from OpenScopeTools import Oscilloscope


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
        print map(ord, cal_values)
        assert cal_values
        assert scope.close_handle()

    def test_read_data(self):
        scope = Oscilloscope()
        assert scope.setup()
        assert scope.open_handle()
        ch1_data, _ = scope.read_data(data_size=0x400)
        ch1_data = map(ord, ch1_data)
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
            ch1_data, ch2_data = scope.read_data(data_size=data_size)
            print len(ch1_data)
            # print map(ord, ch1_data)
            print len(ch2_data)
            # print map(ord, ch2_data)
            assert ch1_data, ch2_data
            data_size <<= 1
        assert scope.close_handle()