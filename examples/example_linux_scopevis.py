__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope
import pylab


def apply_data_smoothing(data, window=1):
    new_data = data[:window]
    for i, point in enumerate(data[window:-window]):
        new_data.append(sum(data[i-window:i+window+1])/(2*window+1))
    new_data.extend(data[-window:])
    return new_data

sample_rate_index = 0x04
voltage_range = 0x01
data_points = 0x2000

scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.set_sample_rate(sample_rate_index)
scope.set_ch1_voltage_range(voltage_range)
ch1_data, _ = scope.read_data(data_points)
voltage_data = scope.scale_read_data(ch1_data, voltage_range)
timing_data, _ = scope.convert_sampling_rate_to_measurement_times(data_points, sample_rate_index)
scope.close_handle()
pylab.title('Scope Visulization Example')
pylab.plot(timing_data, voltage_data, color='#009900', label='Raw Trace')
pylab.plot(timing_data, apply_data_smoothing(voltage_data, window=3), color='#0033CC', label='Smoothed Trace')
pylab.xlabel('Time (s)')
pylab.ylabel('Voltage (V)')
pylab.grid()
pylab.legend(loc='best')
pylab.xticks(rotation=30)
pylab.tight_layout()
pylab.show()

