__author__ = 'rcope'

from PyHT6022.LibUsbScope import Oscilloscope
import pylab


def apply_data_smoothing(data, window=1):
    new_data = data[:window]
    for i, point in enumerate(data[window:-window]):
        new_data.append(sum(data[i-window:i+window+1])/(2*window+1))
    new_data.extend(data[-window:])
    return new_data

scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.set_sample_rate(26)
scope.set_ch1_voltage_range(0x0a)
ch1_data, _ = scope.read_data(0x2000)
voltage_data = scope.scale_read_data(ch1_data, 0x0a)
timing_data, _ = scope.convert_sampling_rate_to_measurement_times(0x2000, 26)
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

