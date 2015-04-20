__author__ = 'Robert Cope'

import usb1
import time

from hantek_firmware import device_firmware


class Oscilloscope(object):
    ALT_VENDOR_ID = 0x04B4
    VENDOR_ID = 0x04B5
    MODEL_ID = 0x6022

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

    def close_handle(self):
        if not self.device_handle:
            return True
        self.device_handle.releaseInterface(0)
        self.device_handle.close()
        self.device_handle = None
        return True

    def __del__(self):
        self.close_handle()

    def flash_firmware(self):
        if not self.device_handle:
            assert self.open_handle()
        for packet in device_firmware:
            bytes_written = self.device_handle.controlWrite(0x40, 0xA0, packet.value, 0x00, packet.data, 0x00)
            assert bytes_written == packet.size
        # After firmware is written, scope will typically show up again as a different device, so scan again
        time.sleep(0.1)
        self.close_handle()
        self.setup()
        self.open_handle()
        return True

    def get_calibration_values(self):
        if not self.device_handle:
            assert self.open_handle()
        return self.device_handle.controlRead(0x40, 0xA2, 0x08, 0x00, 0x10, 30)

