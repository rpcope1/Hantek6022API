__author__ = 'rcope'

from PyHT6022.LibUsbScope import Oscilloscope
import matplotlib.pyplot as plt
import time
import numpy as np
from collections import deque


def build_stability_array(data, threshold=1.0):
    initial = True
    running = False
    current = 0
    stability = []
    for entry in data:
        if initial and entry > threshold:
            continue
        elif initial and entry < threshold:
            initial = False
        elif entry > threshold and not running:
            running = True
            current = 0
        elif entry > threshold and running:
            current += 1
        elif entry < threshold and running:
            stability.append(current)
            running = False
        else:
            continue
    return stability[1:-1]


sample_rate_index = 0x1E
voltage_range = 0x01
data_points = 0x2000

scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.flash_firmware()
scope.set_num_channels(1)
scope.set_sample_rate(sample_rate_index)
scope.set_ch1_voltage_range(voltage_range)
time.sleep(1)

data = deque(maxlen=2*1024*1024)
data_extend = data.extend


def extend_callback(ch1_data, _):
    data_extend(ch1_data)

start_time = time.time()
print "Clearing FIFO and starting data transfer..."
scope.clear_fifo()
shutdown_event = scope.read_async(extend_callback, data_points, outstanding_bulk_transfers=5)
i = 0
while time.time() - start_time < 1:
    print i
    i += 1
    time.sleep(0.01)
print "Stopping new transfers."
shutdown_event.set()
print "Snooze 5"
time.sleep(5)
print "Closing handle"
scope.close_handle()
print "Handle closed."
print "Points in buffer:", len(data)
plt.figure(0)
plt.plot(scope.scale_read_data(data, voltage_range))
plt.figure(1)
plt.plot(np.fft.fft(scope.scale_read_data(data, voltage_range)))
stab = build_stability_array(scope.scale_read_data(data, voltage_range), threshold=1.2)
stab_avg, stab_std = np.average(stab), np.std(stab)
print "Stability", stab_avg, "+/-", stab_std, "({}% deviance)".format(100.0*stab_std/stab_avg)
bad_pulse_count = len([p for p in stab if abs(stab_avg - p) >= stab_std])
print "Pulses more than 1 std dev out: {}/{} ({} %)".format(bad_pulse_count, len(stab), 100.0*bad_pulse_count/len(stab))
print stab
plt.show()