__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope
import time

iterations = 50


def print_report(time_measurements, num_bytes):
    rates = []
    for i, t in enumerate(time_measurements[1:]):
        rate = num_bytes / (t - time_measurements[i])
        rates.append(rate)
    print("Average: {} MB/s".format(sum(rates)/(len(rates)*1e6)))
    return rates

voltage_range = 0x01

time_fxn = time.time

scope = Oscilloscope()
scope.setup()
scope.open_handle()

scope.set_ch1_voltage_range(voltage_range)
for sample_rate_index in [0x30, 0x10, 0x08, 0x04, 0x01, 0x32, 0x14, 0x0A]:
    print('sample_rate_index {}'.format(sample_rate_index))
    scope.set_sample_rate(sample_rate_index)
    _, label = scope.convert_sampling_rate_to_measurement_times(1, sample_rate_index)
    print("Sample rate: {}".format(label))
    print("-"*40)
    for data_points in [0x800, 0x1000, 0x8000, 0x10000, 0x80000, 0x100000, 0x200000]:
        print('data points: {}'.format(data_points))
        reader_fxn = scope.build_data_reader(raw=True)
        times = []
        times_append = times.append
        times_append(time_fxn())
        for _ in range(iterations):
            ch1_data, _ = reader_fxn(data_points)
            times_append(time_fxn())
        print("Raw Mode, Data Points: 0x{:x}".format(data_points))
        print_report(times, data_points)

        reader_fxn = scope.build_data_reader()
        times = []
        times_append = times.append
        times_append(time_fxn())
        for _ in range(iterations):
            ch1_data, _ = reader_fxn(data_points)
            times_append(time_fxn())
        print("List Conversion, Data Points: 0x{:x}".format(data_points))
        print_report(times, data_points)
    print("-"*40)
    print()


scope.close_handle()
