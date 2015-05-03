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
data_points = 3 * 1024

scope = Oscilloscope()
scope.setup()
scope.open_handle()
if (not scope.is_device_firmware_present):
    scope.flash_firmware()
scope.set_interface(1); # choose ISO
scope.set_num_channels(1)
scope.set_sample_rate(sample_rate_index)
scope.set_ch1_voltage_range(voltage_range)
time.sleep(1)

data = deque(maxlen=2*1024*1024)
data_extend = data.extend


def extend_callback(ch1_data, _):
    data_extend(ch1_data)

start_time = time.time()
shutdown_event = scope.read_async(extend_callback, data_points, outstanding_iso_transfers=25)
print "Clearing FIFO and starting data transfer..."
i = 0
scope.start_capture()
while time.time() - start_time < 1:
    time.sleep(0.01)
scope.stop_capture()
print "Stopping new transfers."
shutdown_event.set()
print "Snooze 1"
time.sleep(1)
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
