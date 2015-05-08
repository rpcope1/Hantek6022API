#!/usr/bin/python

from ctypes import *
import os
from struct import pack
import StringIO

# Set the directory for your HantekScope DLL here.
marchdll_file = os.path.join("HantekSDK", "HTMarch.dll")


class Oscilloscope(object):
    def __init__(self, scopeid=0):  # Set up our scope. The scope id is for each scope attached to the system.
        # No Linux support...yet
        if os.name != 'nt':
            raise StandardError('Hantek SDK Oscilloscope wrapper only supports windows!')

        self.marchdll = WinDLL(marchdll_file)
        self.scopeid = c_ushort(scopeid)
        self.channels = {1: 0, 2: 1}
        self.volt_indicies = {0: ("20 mV/Div", 20e-3), 1: ("50 mV/Div", 50e-3), 2: ("100 mV/Div", 0.1),
                              3: ("200 mV/Div", 0.2),
                              4: ("500 mV/Div", 0.5), 5: ("1 V/Div", 1.0), 6: ("2 V/Div", 2.0), 7: ("5 V/Div", 5.0)}

        init_volt = 4
        self.current_volt_index = [None, None, None]  # Use a list instead of dict for speed up on data reads.
        # No channel 0, so let's just make that None.
        for chan in self.channels:
            self.current_volt_index[chan] = c_int(init_volt)  # Just set it to some initial value.

        self.current_volt_div = [None, None, None]
        for chan in self.channels:
            self.current_volt_div[chan] = self.volt_indicies[init_volt][1]

        self.sample_rate_indicies = {11: ("16 MSa/s", 16e6), 12: ("8 MSa/s", 8e6), 13: ("4 MSa/s", 4e6),
                                     25: ("500 KSa/s", 500e3), 26: ("200 KSa/s", 200e3), 27: ("100 KSa/s", 100e3)}
        for index in range(0, 11):
            self.sample_rate_indicies[index] = ("48 MSa/s", 48e6)  # All values 0-10 are set to this.
        for index in range(14, 25):
            self.sample_rate_indicies[index] = ("1 MSa/s", 1e6)

        init_rate = 10
        self.current_sample_rate_index = c_int(init_rate)
        self.current_sample_rate = self.sample_rate_indicies[init_rate][1]

        self.valid_trigger_sweeps = {0: "Auto", 1: "Normal", 2: "Single"}
        self.current_trigger_sweep = c_short(0)

        self.valid_trigger_source = {0: "CH1", 1: "CH2"}
        self.current_trigger_source = c_short(0)

        self.valid_trigger_slopes = {0: "Rise", 1: "Fall"}
        self.current_trigger_slope = c_short(0)

        self.valid_htrigger_position = range(0, 101)
        self.current_htrigger_position = c_short(10)

        self.valid_trigger_levels = range(0, 256)
        self.current_trigger_level = c_short(10)

        self.valid_dvalue_modes = {0: "Step D-Value", 1: "Line D-Value", 2: "sin(x)/x D-Value"}
        self.current_dvalue_mode = c_short(0)

        self.cal_data = None

    def is_attached(self):
        """
            Takes no arguments.
            Returns true if the scope is attached, false otherwise.
        """
        retval = self.marchdll.dsoOpenDevice(self.scopeid)
        if not retval:
            return False
        elif retval == 1:
            return True
        else:
            print "ERROR: Unexpected return value through API."
            return False

    def get_voltage_div_dict(self):
        """
            Takes no arguments, returns the dictionary that relates voltage index to its
            corresponding voltage division.
        """
        return self.volt_indicies

    def get_channels_dict(self):
        """Takes no arguments, returns the dictionary that contains all valid channels."""
        return self.channels

    def get_sample_rate_dict(self):
        """
            Takes no arguments, returns the dictionary that relates sample index to its
            corresponding timing division.
        """
        return self.sample_rate_indicies

    def get_trigger_sweeps_dict(self):
        """
            Takes no arguments, returns the dictionary that relates the trigger sweep index to its
            corresponding setting.
        """
        return self.valid_trigger_sweeps

    def get_trigger_sources_dict(self):
        """
            Takes no arguments, returns the dictionary that relates the trigger source index to its
            corresponding setting.
        """
        return self.valid_trigger_source

    def get_trigger_slopes_dict(self):
        """
            Takes no arguments, returns the dictionary that relates the trigger slope index to its
            corresponding setting.
        """
        return self.valid_trigger_slopes

    def set_voltage_division(self, channel_num, volt_index):
        """
            Takes two arguments, first the channel number, second the voltage index value.
            Returns true if arguments were valid and command returned successfully, false otherwise.
        """
        if channel_num not in self.channels or volt_index not in self.volt_indicies:
            return False
        else:
            self.current_volt_index[channel_num] = c_int(volt_index)
            self.current_volt_div[channel_num] = self.volt_indicies[volt_index][1]
            retval = self.marchdll.dsoSetVoltDIV(self.scopeid,
                                                 c_int(self.channels[channel_num]),
                                                 self.current_volt_index[channel_num])
            if retval == 1:
                return True  # The DLL documentation may contain a typo on the return val.
            else:
                return False

    def set_sampling_rate(self, sample_rate_index):
        """
            Takes one arguments,the sampling rate index value.
            Returns true if arguments were valid and command returned successfully, false otherwise.
        """
        if sample_rate_index not in self.sample_rate_indicies:
            return False
        else:
            self.current_sample_rate_index = c_int(sample_rate_index)
            self.current_sample_rate = self.sample_rate_indicies[sample_rate_index][1]
            retval = self.marchdll.dsoSetTimeDIV(self.scopeid,
                                                 self.current_sample_rate_index)
            if retval == 1:
                return True  # The DLL documentation may contain a typo on the return val.
            else:
                return False

    @staticmethod
    def convert_read_data(input_data, scale, scale_points=32.0):
        """
            Helper function for converting the data taken from the scope into its true analog representation.
            Takes input from scope data, and the scaling factor, with the optional number of points in the
            scaling division. Returns an array of analog values read from the scope.
        """
        point_div = scale / scale_points
        out = [0.0 for _ in input_data]
        input_data = [j.value for j in input_data]
        for j in xrange(0, len(input_data)):
            out[j] = input_data[j] * point_div
        return input_data

    def read_data_from_scope(self, data_points=500, display_points=500, raw_data=False):
        """
            Takes two optional arguments, number of data points and number of display point
            to grab. Returns a tuple with channel 1 data, channel 2 data, time since capture init, and a trigger
            index on success, and None on failure.
        """
        if self.cal_data == None:
            return None
        else:
            data_ch1 = (c_short * data_points)()
            data_ch2 = (c_short * data_points)()

            t_index = c_ulong(0)

            retval = self.marchdll.dsoReadHardData(self.scopeid,
                                                   byref(data_ch1),
                                                   byref(data_ch2),
                                                   c_ulong(data_points),
                                                   byref(self.cal_data),
                                                   self.current_volt_index[1],
                                                   self.current_volt_index[2],
                                                   self.current_trigger_sweep,
                                                   self.current_trigger_source,
                                                   self.current_trigger_level,
                                                   self.current_trigger_slope,
                                                   self.current_sample_rate_index,
                                                   self.current_htrigger_position,
                                                   c_ulong(display_points),
                                                   byref(t_index),
                                                   self.current_dvalue_mode)
            if retval == -1:
                return None
            elif raw_data:
                return data_ch1, data_ch2, [j / 1e6 for j in range(0, data_points)], t_index
            else:
                return (self.convert_read_data(data_ch1, self.current_volt_div[1]),
                        self.convert_read_data(data_ch2, self.current_volt_div[2]),
                        [j / 1e6 for j in range(0, data_points)],
                        t_index)

    def setup_dso_cal_level(self):
        """
            This function takes no arguments, and returns true on success, false on failure.
            This is used to poll the oscilloscope's calibration level.
        """
        if self.cal_data is None:
            self.cal_data = (c_short * 32)()
        retval = self.marchdll.dsoGetCalLevel(self.scopeid, byref(self.cal_data), c_short(32))
        if retval == 0:
            return True
        else:
            print "setupDsoCalLevel retval: ", retval
            return False

    def calibrate_dso(self):
        """
            This function takes no arguments, and returns true on success, false on failure.
            This is used to set the oscilloscope's calibration level.
        """
        if self.cal_data is None:
            self.cal_data = (c_short * 32)()
        retval = self.marchdll.dsoCalibrate(self.scopeid, self.current_sample_rate_index,
                                            self.current_volt_index[1], self.current_volt_index[2],
                                            byref(self.cal_data))
        if retval == 0:
            return True
        else:
            return False

    def get_calibration_data(self):
        """
            This function takes no arguments, and returns the current state of calibration data.
            If None is returned, no calibration settings were loaded.
            This could be called after the calibrateDso function.
        """
        return self.cal_data

    def set_dso_calibration(self, cal_data):
        """This function takes one argument and returns True on success, False on failure.
            The argument is a previous calibration to be loaded to the device. This function sets
            the calibration level."""
        if type(cal_data) is not type((c_short * 32)()):
            return False
        else:
            self.cal_data = cal_data
            retval = self.marchdll.dsoSetCalLevel(self.scopeid, byref(self.cal_data), 32)
            if retval == 0:
                return True
            else:
                return False


# TODO: Make this into real unit tests.
if __name__ == "__main__":
    scope = Oscilloscope()
    print "Running Unit tests..."
    print "Test 1 -> Test Device Attached function."
    print scope.is_attached(), "<-should be true if a scope is attached."
    print Oscilloscope(scopeid=1).is_attached(), "<-should be false if 1 or less scopes are attached."
    print
    print "Valid Voltage Division settings:", scope.get_voltage_div_dict()
    print
    print "Valid Channels", scope.get_channels_dict()
    print
    print "Valid Sampling Rate,", scope.get_sample_rate_dict()
    print
    print scope.set_voltage_division(100, 200), "<-should return false."
    print scope.set_voltage_division(1, 6), "<-should return true."
    print scope.set_sampling_rate(500), "<-should return false."
    samplerate = 1000 * 1000
    print scope.set_sampling_rate(24), "<-should return true."
    print scope.read_data_from_scope(), "<-should return None."
    print scope.setup_dso_cal_level(), "<-should return True."
    calLevel = scope.get_calibration_data()
    print "Loaded calibration level:", [int(i) for i in calLevel]
    print scope.set_dso_calibration(calLevel), "<-should return True."
    print "\n------------------\n\tData Tests\t\n------------------\n"
    print "\tVolt Div == 2.0 V, Sample Rate = 1000 KSa/s\n"
    print "------------------\n"
    data = []
    total = 0
    for x in range(0, 10):
        print x
        data.append(scope.read_data_from_scope(1047550, raw_data=True)[0])
        total += len(data[x])

    filename = "test.wav"
    wav_file = open(filename, "wb")
    wav_file.write("RIFF")
    wav_file.write(pack("<L", 44 + total - 8))
    wav_file.write("WAVE")
    wav_file.write("fmt \x10\x00\x00\x00\x01\x00\x01\x00")
    wav_file.write(pack("<L", samplerate))
    wav_file.write(pack("<L", samplerate))
    wav_file.write("\x01\x00\x08\x00")
    wav_file.write("data")
    wav_file.write(pack("<L", total))
    raw = StringIO.StringIO()
    for x in data:
        for v in x:
            raw.write(pack("<B", v & 0xff))
    wav_file.write(raw.getvalue())
    raw.close()
    wav_file.close()
