__author__ = 'Robert Cope', 'Jochen Hoenicke'

import time
import array
import usb1

from PyHT6022.HantekFirmware import default_firmware, fx2_ihex_to_control_packets


class Oscilloscope(object):
    NO_FIRMWARE_VENDOR_ID = 0x04B4
    FIRMWARE_PRESENT_VENDOR_ID = 0x04B5
    MODEL_ID = 0x6022

    RW_FIRMWARE_REQUEST = 0xa0
    RW_FIRMWARE_INDEX = 0x00

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

    SET_NUMCH_REQUEST = 0xe4
    SET_NUMCH_VALUE = 0x00
    SET_NUMCH_INDEX = 0x00

    SAMPLE_RATES = {0x0A: ("100 KS/s", 100e3),
                    0x14: ("200 KS/s", 200e3),
                    0x32: ("500 KS/s", 500e3),
                    0x01: ("1 MS/s", 1e6),
                    0x04: ("4 MS/s", 4e6),
                    0x08: ("8 MS/s", 8e6),
                    0x10: ("16 MS/s", 16e6),
                    0x30: ("24 MS/s", 24e6)}

    VOLTAGE_RANGES = {0x01: ('+/- 5V', 0.0390625, 2.5),
                      0x02: ('+/- 2.5V', 0.01953125, 1.25),
                      0x05: ('+/- 1V', 0.0078125, 0.5),
                      0x0a: ('+/- 500mV', 0.00390625, 0.25)}

    def __init__(self, scope_id=0):
        self.device = None
        self.device_handle = None
        self.context = None
        self.is_device_firmware_present = False
        self.supports_single_channel = False
        self.num_channels = 2
        self.scope_id = scope_id

    def setup(self):
        """
        Attempt to find a suitable scope to run.
        :return: True if a 6022BE scope was found, False otherwise.
        """
        self.context = usb1.USBContext()

        self.device = self.context.getByVendorIDAndProductID(self.FIRMWARE_PRESENT_VENDOR_ID, self.MODEL_ID,
                                                             skip_on_error=True, skip_on_access_error=True) or \
            self.context.getByVendorIDAndProductID(self.NO_FIRMWARE_VENDOR_ID, self.MODEL_ID, skip_on_error=True,
                                                   skip_on_access_error=True)

        if not self.device:
            return False
        self.is_device_firmware_present = self.device.getVendorID() == self.FIRMWARE_PRESENT_VENDOR_ID
        return True

    def open_handle(self):
        """
        Open a device handle for the scope. This needs to occur before sending any commands.
        :return: True if successful, False otherwise. May raise various libusb exceptions on fault.
        """
        if self.device_handle:
            return True
        if not self.device or not self.setup():
            return False
        self.device_handle = self.device.open()
        if self.device_handle.kernelDriverActive(0):
            self.device_handle.detachKernelDriver(0)
        self.device_handle.claimInterface(0)
        if self.is_device_firmware_present:
            self.set_num_channels(2)
        return True

    def close_handle(self, release_interface=True):
        """
        Close the current scope device handle. This should always be called at clean-up.
        :param release_interface: (OPTIONAL) Attempt to release the interface, if we still have it.
        :return: True if successful. May assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            return True
        if release_interface:
            self.device_handle.releaseInterface(0)
        self.device_handle.close()
        self.device_handle = None
        return True

    def __del__(self):
        self.close_handle()

    def flash_firmware(self, firmware=default_firmware, supports_single_channel=True, timeout=60):
        """
        Flash scope firmware to the target scope device. This needs to occur once when the device is first attached,
        as the 6022BE does not have any persistant storage.
        :param firmware: (OPTIONAL) The firmware packets to send. Default: Stock firmware.
        :param supports_single_channel: (OPTIONAL) Set this to false if loading the stock firmware, as it does not
                                        support reducing the number of active channels.
        :param timeout: (OPTIONAL) A timeout for each packet transfer on the firmware upload. Default: 60 seconds.
        :return: True if the correct device vendor was found after flashing firmware, False if the default Vendor ID
                 was present for the device. May assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        for packet in firmware:
            bytes_written = self.device_handle.controlWrite(0x40, self.RW_FIRMWARE_REQUEST,
                                                            packet.value, self.RW_FIRMWARE_INDEX,
                                                            packet.data, timeout=timeout)
            assert bytes_written == packet.size
        # After firmware is written, scope will typically show up again as a different device, so scan again
        time.sleep(0.1)
        self.close_handle(release_interface=False)
        self.setup()
        self.supports_single_channel = supports_single_channel
        self.open_handle()
        return self.is_device_firmware_present

    def flash_firmware_from_hex(self, hex_file, timeout=60):
        """
        Open an Intel hex file for the 8051 and try to flash it to the scope.
        :param hex_file: The hex file to load for flashing.
        :param timeout: (OPTIONAL) A timeout for each packet transfer on the firmware upload. Default: 60 seconds.
        :return: True if the correct device vendor was found after flashing firmware, False if the default Vendor ID
                 was present for the device. May assert or raise various libusb errors if something went wrong.
        """
        return self.flash_firmware(firmware=fx2_ihex_to_control_packets(hex_file), timeout=timeout)

    def read_firmware(self, to_ihex=True, chunk_len=16, timeout=60):
        """
        Read the entire device RAM, and return a raw string.
        :param to_ihex: (OPTIONAL) Convert the firmware into the Intel hex format after reading. Otherwise, return
                        the firmware is a raw byte string. Default: True
        :param chunk_len: (OPTIONAL) The length of RAM chunks to pull from the device at a time. Default: 16 bytes.
        :param timeout: (OPTIONAL) A timeout for each packet transfer on the firmware upload. Default: 60 seconds.
        :return: The raw device firmware, if successful.
                 May assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()

        bytes_written = self.device_handle.controlWrite(0x40, self.RW_FIRMWARE_REQUEST,
                                                        0xe600, self.RW_FIRMWARE_INDEX,
                                                        '\x01', timeout=timeout)
        assert bytes_written == 1
        firmware_chunk_list = []
        # TODO: Fix this for when 8192 isn't divisible by chunk_len
        for packet in range(0, 8192/chunk_len):
            chunk = self.device_handle.controlRead(0x40, self.RW_FIRMWARE_REQUEST,
                                                   packet * chunk_len, self.RW_FIRMWARE_INDEX,
                                                   16, timeout=timeout)
            firmware_chunk_list.append(chunk)
            assert len(chunk) == 16
        bytes_written = self.device_handle.controlWrite(0x40, self.RW_FIRMWARE_REQUEST,
                                                        0xe600, self.RW_FIRMWARE_INDEX,
                                                        '\x00', timeout=timeout)
        assert bytes_written == 1
        if not to_ihex:
            return ''.join(firmware_chunk_list)
        else:
            lines = []
            for i, chunk in enumerate(firmware_chunk_list):
                addr = i*chunk_len
                iterable_chunk = array.array('B', chunk)
                hex_data = "".join(["{:02x}".format(b) for b in iterable_chunk])
                total_sum = (sum(iterable_chunk) + chunk_len + (addr % 256) + (addr >> 8)) % 256
                checksum = (((0xFF ^ total_sum) & 0xFF) + 0x01) % 256
                line = ":{nbytes:02x}{addr:04x}{itype:02x}{hex_data}{checksum:02x}".format(nbytes=chunk_len,
                                                                                           addr=addr,
                                                                                           itype=0x00,
                                                                                           hex_data=hex_data,
                                                                                           checksum=checksum)
                lines.append(line)
            # Add stop record at the end.
            lines.append(":00000001ff")
            return "\n".join(lines)

    def get_calibration_values(self, timeout=0):
        """
        Retrieve the current calibration values from the oscilloscope.
        :param timeout: (OPTIONAL) A timeout for the transfer. Default: 0 (No timeout)
        :return: A 32 single byte int list of calibration values, if successful.
                 May assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        cal_string = self.device_handle.controlRead(0x40, self.RW_CALIBRATION_REQUEST, self.RW_CALIBRATION_VALUE,
                                                    self.RW_CALIBRATION_INDEX, 0x20, timeout=timeout)
        return array.array('B', cal_string)

    def set_calibration_values(self, cal_list, timeout=0):
        """
        Set the a calibration level for the oscilloscope.
        :param cal_list: The list of calibration values, should usually be 32 single byte ints.
        :param timeout: (OPTIONAL) A timeout for the transfer. Default: 0 (No timeout)
        :return: True if successful. May assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        cal_list = cal_list if isinstance(cal_list, basestring) else array.array('c', cal_list).tostring()
        data_len = self.device_handle.controlWrite(0x40, self.RW_CALIBRATION_REQUEST, self.RW_CALIBRATION_VALUE,
                                                   self.RW_CALIBRATION_INDEX, cal_list, timeout=timeout)
        assert data_len == len(cal_list)
        return True

    def read_data(self, data_size=0x400, raw=False, clear_fifo=True, timeout=0):
        """
        Read both channel's ADC data from the device. No trigger support, you need to do this in software.
        :param data_size: (OPTIONAL) The number of data points for each channel to retrieve. Default: 0x400 points.
        :param raw: (OPTIONAL) Return the raw bytestrings from the scope. Default: Off
        :param clear_fifo: (OPTIONAL) Clear the scope's FIFO buffer, causing all data returned to start immediately
                           after.
        :param timeout: (OPTIONAL) The timeout for each bulk transfer from the scope. Default: 0 (No timeout)
        :return: If raw, two bytestrings are returned, the first for CH1, the second for CH2. If raw is off, two
                 lists are returned (by iterating over the bytestrings and converting to ordinals). The lists contain
                 the ADC value measured at that time, which should be between 0 - 255.

                 If you'd like nicely scaled data, just dump the return lists into the scale_read_data method which
                 your current voltage range setting.

                 This method may assert or raise various libusb errors if something went wrong.
        """
        data_size *= self.num_channels
        if not self.device_handle:
            assert self.open_handle()
        if clear_fifo:
            self.device_handle.controlRead(0x40, 0xe3, 0x00, 0x00, 0x01, timeout=timeout)
        data = self.device_handle.bulkRead(0x86, data_size, timeout=timeout)
        if self.num_channels == 2:
            chdata = data[::2], data[1::2]
        else:
            chdata = data, ''
        if raw:
            return chdata
        else:
            return array.array('B', chdata[0]), array.array('B', chdata[1])

    def build_data_reader(self, raw=False, clear_fifo=True):
        """
        Build a (slightly) more optimized reader closure, for (slightly) better performance.
        :param raw: (OPTIONAL) Return the raw bytestrings from the scope. Default: Off
        :param clear_fifo: (OPTIONAL) Clear the FIFO buffer on the device on the read, restarting data collection.
        :return: A fast_read_data function, which behaves much like the read_data function. The fast_read_data
                 function returned takes two parameters:
                 :param data_size: Number of data points to return (1 point <-> 1 byte).
                 :param timeout: (OPTIONAL) The timeout for each bulk transfer from the scope. Default: 0 (No timeout)
                 :return:  If raw, two bytestrings are returned, the first for CH1, the second for CH2. If raw is off,
                 two lists are returned (by iterating over the bytestrings and converting to ordinals).
                 The lists contain the ADC value measured at that time, which should be between 0 - 255.

        This method and the closure may assert or raise various libusb errors if something went/goes wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        scope_control_read = self.device_handle.controlRead
        scope_bulk_read = self.device_handle.bulkRead
        array_builder = array.array
        if self.num_channels == 1 and raw and clear_fifo:
            def fast_read_data(data_size, timeout=0):
                scope_control_read(0x40, 0xe3, 0x00, 0x00, 0x01, timeout)
                data = scope_bulk_read(0x86, data_size, timeout)
                return data, ''
        elif self.num_channels == 1 and raw and not clear_fifo:
            def fast_read_data(data_size, timeout=0):
                data = scope_bulk_read(0x86, data_size, timeout)
                return data, ''
        elif self.num_channels == 1 and not raw and clear_fifo:
            def fast_read_data(data_size, timeout=0):
                scope_control_read(0x40, 0xe3, 0x00, 0x00, 0x01, timeout)
                data = scope_bulk_read(0x86, data_size, timeout)
                return array_builder('B', data), array_builder('B', '')
        elif self.num_channels == 1 and not raw and not clear_fifo:
            def fast_read_data(data_size, timeout=0):
                data = scope_bulk_read(0x86, data_size, timeout)
                return array_builder('B', data), array_builder('B', '')
        elif self.num_channels == 2 and raw and clear_fifo:
            def fast_read_data(data_size, timeout=0):
                data_size <<= 0x1
                scope_control_read(0x40, 0xe3, 0x00, 0x00, 0x01, timeout)
                data = scope_bulk_read(0x86, data_size, timeout)
                return data[::2], data[1::2]
        elif self.num_channels == 2 and raw and not clear_fifo:
            def fast_read_data(data_size, timeout=0):
                data_size <<= 0x1
                data = scope_bulk_read(0x86, data_size, timeout)
                return data[::2], data[1::2]
        elif self.num_channels == 2 and not raw and clear_fifo:
            def fast_read_data(data_size, timeout=0):
                data_size <<= 0x1
                scope_control_read(0x40, 0xe3, 0x00, 0x00, 0x01, timeout)
                data = scope_bulk_read(0x86, data_size, timeout)
                return array_builder('B', data[::2]), array_builder('B', data[1::2])

        elif self.num_channels == 2 and not raw and not clear_fifo:
            def fast_read_data(data_size, timeout=0):
                data_size <<= 0x1
                data = scope_bulk_read(0x86, data_size, timeout)
                return array_builder('B', data[::2]), array_builder('B', data[1::2])
        else:
            # Should never be here.
            assert False
        return fast_read_data

    @staticmethod
    def scale_read_data(read_data, voltage_range, probe_multiplier=1):
        """
        Convenience function for converting data read from the scope to nicely scaled voltages.
        :param read_data: The list of points returned from the read_data functions.
        :param voltage_range: The voltage range current set for the channel.
        :param probe_multiplier: (OPTIONAL) An additonal multiplictive factor for changing the probe impedance.
                                 Default: 1
        :return: A list of correctly scaled voltages for the data.
        """
        scale_factor = (5.0 * probe_multiplier)/(voltage_range << 7)
        return [(datum - 128)*scale_factor for datum in read_data]

    def set_sample_rate(self, rate_index, timeout=0):
        """
        Set the sample rate index for the scope to sample at. This determines the time between each point the scope
        returns.
        :param rate_index: The rate_index. These are the keys for the SAMPLE_RATES dict for the Oscilloscope object.
                           Common rate_index values and actual sample rate per channel:
                           0x0A <-> 100 KS/s
                           0x14 <-> 200 KS/s
                           0x32 <-> 500 KS/s
                           0x01 <-> 1 MS/s
                           0x04 <-> 4 MS/s
                           0x08 <-> 8 MS/s
                           0x10 <-> 16 MS/s
                           0x30 <-> 24 MS/s

                           Outside of the range spanned by these values, and those listed in the SAMPLE_RATES dict, it
                           is not know how a value such as 0x29 or 0x28 will affect the behavior of the scope.
        :param timeout: (OPTIONAL) An additonal multiplictive factor for changing the probe impedance.
        :return: True if successful. This method may assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        bytes_written = self.device_handle.controlWrite(0x40, self.SET_SAMPLE_RATE_REQUEST,
                                                        self.SET_SAMPLE_RATE_VALUE, self.SET_SAMPLE_RATE_INDEX,
                                                        chr(rate_index), timeout=timeout)
        assert bytes_written == 0x01
        return True

    def convert_sampling_rate_to_measurement_times(self, num_points, rate_index):
        """
        Convenience method for converting a sampling rate index into a list of times from beginning of data collection
        and getting human-readable sampling rate string.
        :param num_points: The number of data points.
        :param rate_index: The sampling rate index used for data collection.
        :return: A list of times in seconds from beginning of data collection, and the nice human readable rate label.
        """
        rate_label, rate = self.SAMPLE_RATES.get(rate_index, ("? MS/s", 1.0))
        return [i/rate for i in xrange(num_points)], rate_label

    def set_num_channels(self, nchannels, timeout=0):
        """
        Set the number of active channels.  Either we sample only CH1 or we
        sample CH1 and CH2.
        :param nchannels: The number of active channels.  This is 1 or 2.
        :param timeout: (OPTIONAL) An additonal multiplictive factor for changing the probe impedance.
        :return: True if successful. This method may assert or raise various libusb errors if something went wrong.
        """
        if self.supports_single_channel:
            assert nchannels == 1 or nchannels == 2
            if not self.device_handle:
                assert self.open_handle()
            bytes_written = self.device_handle.controlWrite(0x40, self.SET_NUMCH_REQUEST,
                                                            self.SET_NUMCH_VALUE, self.SET_NUMCH_INDEX,
                                                            chr(nchannels), timeout=timeout)
            assert bytes_written == 0x01
            self.num_channels = nchannels
            return True
        else:
            return False

    def set_ch1_voltage_range(self, range_index, timeout=0):
        """
        Set the voltage scaling factor at the scope for channel 1 (CH1).
        :param range_index: A numerical constant, which determines the devices range by the following formula:
                            range := +/- 5.0 V / (range_indeX).

                            The stock software only typically uses the range indicies 0x01, 0x02, 0x05, and 0x0a,
                            but others, such as 0x08 and 0x0b seem to work correctly.

                            This same range_index is given to the scale_read_data method to get nicely scaled
                            data in voltages returned from the scope.

        :param timeout: (OPTIONAL) An additonal multiplictive factor for changing the probe impedance.
        :return: True if successful. This method may assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        bytes_written = self.device_handle.controlWrite(0x40, self.SET_CH1_VR_REQUEST,
                                                        self.SET_CH1_VR_VALUE, self.SET_CH1_VR_INDEX,
                                                        chr(range_index), timeout=timeout)
        assert bytes_written == 0x01
        return True

    def set_ch2_voltage_range(self, range_index, timeout=0):
        """
        Set the voltage scaling factor at the scope for channel 1 (CH1).
        :param range_index: A numerical constant, which determines the devices range by the following formula:
                            range := +/- 5.0 V / (range_indeX).

                            The stock software only typically uses the range indicies 0x01, 0x02, 0x05, and 0x0a,
                            but others, such as 0x08 and 0x0b seem to work correctly.

                            This same range_index is given to the scale_read_data method to get nicely scaled
                            data in voltages returned from the scope.

        :param timeout: (OPTIONAL) An additonal multiplictive factor for changing the probe impedance.
        :return: True if successful. This method may assert or raise various libusb errors if something went wrong.
        """
        if not self.device_handle:
            assert self.open_handle()
        bytes_written = self.device_handle.controlWrite(0x40, self.SET_CH2_VR_REQUEST,
                                                        self.SET_CH2_VR_VALUE, self.SET_CH2_VR_INDEX,
                                                        chr(range_index), timeout=timeout)
        assert bytes_written == 0x01
        return True
