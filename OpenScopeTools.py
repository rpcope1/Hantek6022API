__author__ = 'Robert Cope'

import usb1
import time

from hantek_firmware import device_firmware


class Oscilloscope(object):
    ALT_VENDOR_ID = 0x04B4
    VENDOR_ID = 0x04B5
    MODEL_ID = 0x6022

    UPLOAD_FIRMWARE_REQUEST = 0xa0
    UPLOAD_FIRMWARE_INDEX = 0x00

    RW_CALIBRATION_REQUEST = 0xa2
    RW_CALIBRATION_VALUE = 0x08
    RW_CALIBRATION_INDEX = 0x00

    SET_SAMPLE_RATE_REQUEST = 0xe2
    SET_SAMPLE_RATE_VALUE = 0x00
    SET_SAMPLE_RATE_INDEX = 0x00

    SET_CH1_VR_REQUEST = 0xe0
    SET_CH1_VR_VALUE = 0x00
    SET_CH1_VR_INDEX = 0x00

    SET_CH2_VR_REQUEST = 0xe1
    SET_CH2_VR_VALUE = 0x00
    SET_CH2_VR_INDEX = 0x00

    SAMPLE_RATES = {0: ("48 MS/s", 48e6),
                    1: ("48 MS/s", 48e6),
                    2: ("48 MS/s", 48e6),
                    3: ("48 MS/s", 48e6),
                    4: ("48 MS/s", 48e6),
                    5: ("48 MS/s", 48e6),
                    6: ("48 MS/s", 48e6),
                    7: ("48 MS/s", 48e6),
                    8: ("48 MS/s", 48e6),
                    9: ("48 MS/s", 48e6),
                    10: ("48 MS/s", 48e6),
                    11: ("16 MSa/s", 16e6),
                    12: ("8 MSa/s", 8e6),
                    13: ("4 MSa/s", 4e6),
                    14: ("1 MS/s", 1e6),
                    15: ("1 MS/s", 1e6),
                    16: ("1 MS/s", 1e6),
                    17: ("1 MS/s", 1e6),
                    18: ("1 MS/s", 1e6),
                    19: ("1 MS/s", 1e6),
                    20: ("1 MS/s", 1e6),
                    21: ("1 MS/s", 1e6),
                    22: ("1 MS/s", 1e6),
                    23: ("1 MS/s", 1e6),
                    24: ("1 MS/s", 1e6),
                    25: ("500 KSa/s", 500e3),
                    26: ("200 KSa/s", 200e3),
                    27: ("100 KSa/s", 100e3)}

    VOLTAGE_RANGES = {0x01: ('+/- 5V', 0.0390625, 2.5),
                      0x02: ('+/- 2.5V', 0.01953125, 1.25),
                      0x05: ('+/- 1V', 0.0078125, 0.5),
                      0x0a: ('+/- 500mV', 0.00390625, 0.25)}

    def __init__(self, scope_id=0):
        self.device = None
        self.device_handle = None
        self.scope_id = scope_id

    def setup(self):
        context = usb1.USBContext()
        self.device = context.getByVendorIDAndProductID(self.VENDOR_ID, self.MODEL_ID, skip_on_error=True,
                                                        skip_on_access_error=True) or \
            context.getByVendorIDAndProductID(self.ALT_VENDOR_ID, self.MODEL_ID, skip_on_error=True,
                                              skip_on_access_error=True)

        if not self.device:
            return False
        return True

    def open_handle(self):
        if self.device_handle:
            return True
        if not self.device or not self.setup():
            return False
        self.device_handle = self.device.open()
        if self.device_handle.kernelDriverActive(0):
            self.device_handle.detachKernelDriver(0)
        self.device_handle.claimInterface(0)
        return True

    def close_handle(self, release_interface=True):
        if not self.device_handle:
            return True
        if release_interface:
            self.device_handle.releaseInterface(0)
        self.device_handle.close()
        self.device_handle = None
        return True

    def __del__(self):
        self.close_handle()

    def flash_firmware(self, firmware=device_firmware, timeout=60):
        if not self.device_handle:
            assert self.open_handle()
        for packet in firmware:
            bytes_written = self.device_handle.controlWrite(0x40, self.UPLOAD_FIRMWARE_REQUEST,
                                                            packet.value, self.UPLOAD_FIRMWARE_INDEX,
                                                            packet.data, timeout=timeout)
            assert bytes_written == packet.size
        # After firmware is written, scope will typically show up again as a different device, so scan again
        time.sleep(0.1)
        self.close_handle(release_interface=False)
        self.setup()
        self.open_handle()
        return True

    def get_calibration_values(self, timeout=0):
        if not self.device_handle:
            assert self.open_handle()
        return self.device_handle.controlRead(0x40, self.RW_CALIBRATION_REQUEST, self.RW_CALIBRATION_VALUE,
                                              self.RW_CALIBRATION_INDEX, 0x20, timeout=timeout)

    def set_calibration_values(self, cal_list, timeout=0):
        if not self.device_handle:
            assert self.open_handle()
        cal_list = cal_list if isinstance(cal_list, basestring) else "".join(map(chr, cal_list))
        return self.device_handle.controlRead(0x40, self.RW_CALIBRATION_REQUEST, self.RW_CALIBRATION_VALUE,
                                              self.RW_CALIBRATION_INDEX, cal_list, timeout=timeout)

    def read_data(self, data_size=0x400, raw=False, timeout=0):
        data_size <<= 0x1
        if not self.device_handle:
            assert self.open_handle()
        self.device_handle.controlRead(0x40, 0xe3, 0x00, 0x00, 0x01, timeout=timeout)
        data = self.device_handle.bulkRead(0x86, data_size, timeout=timeout)
        if raw:
            return data[::2], data[1::2]
        else:
            return map(ord, data[::2]), map(ord, data[1::2])

    @staticmethod
    def scale_read_data(read_data, voltage_range):
        scale_factor = 5.0/(voltage_range << 7)
        return [(datum - 128)*scale_factor for datum in read_data]

    def set_sample_rate(self, rate_index, timeout=0):
        if not self.device_handle:
            assert self.open_handle()
        bytes_written = self.device_handle.controlWrite(0x40, self.SET_SAMPLE_RATE_REQUEST,
                                                        self.SET_SAMPLE_RATE_VALUE, self.SET_SAMPLE_RATE_INDEX,
                                                        chr(rate_index), timeout=timeout)
        assert bytes_written == 0x01
        return True

    def set_ch1_voltage_range(self, range_index, timeout=0):
        if not self.device_handle:
            assert self.open_handle()
        bytes_written = self.device_handle.controlWrite(0x40, self.SET_CH1_VR_REQUEST,
                                                        self.SET_CH1_VR_VALUE, self.SET_CH1_VR_INDEX,
                                                        chr(range_index), timeout=timeout)
        assert bytes_written == 0x01
        return True

    def set_ch2_voltage_range(self, range_index, timeout=0):
        if not self.device_handle:
            assert self.open_handle()
        bytes_written = self.device_handle.controlWrite(0x40, self.SET_CH2_VR_REQUEST,
                                                        self.SET_CH2_VR_VALUE, self.SET_CH2_VR_INDEX,
                                                        chr(range_index), timeout=timeout)
        assert bytes_written == 0x01
        return True