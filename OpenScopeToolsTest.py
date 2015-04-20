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