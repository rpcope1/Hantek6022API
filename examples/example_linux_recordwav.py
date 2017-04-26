from __future__ import print_function

__author__ = 'Robert Cope', 'Jochen Hoenicke'
# This code was used to help execute a side-channel attack on the Trezor Bitcoin wallet.
# See more: http://johoe.mooo.com/trezor-power-analysis/
# Original Author: Jochen Hoenicke

from struct import pack
import sys
import time
from collections import deque

from PyHT6022.LibUsbScope import Oscilloscope

voltagerange = 10       # 1 (5V), 2 (2.6V), 5 or 10
samplerate = 24         # sample rate in MHz or in 10khz
numchannels = 1
numseconds = 8          # number of seconds to sample
blocksize = 6*1024      # should be divisible by 6*1024
alternative = 1         # choose ISO 3072 bytes per 125 us

scope = Oscilloscope()
scope.setup()
scope.open_handle()
if (not scope.is_device_firmware_present):
    scope.flash_firmware()
else:
    scope.supports_single_channel = True;
print("Setting up scope!")

scope.set_interface(alternative);
print("ISO" if scope.is_iso else "BULK", "packet size:", scope.packetsize)
scope.set_num_channels(numchannels)
# set voltage range
scope.set_ch1_voltage_range(voltagerange)
# set sample rate
scope.set_sample_rate(samplerate)
# we divide by 100 because otherwise audacity lets us not zoom into it
samplerate = samplerate * 1000 * 10

print("Reading data from scope! in ",)
for x in range(3):
    print(3-x,"..",)
    sys.stdout.flush()
    time.sleep(1)
print("now")

data = []
data_extend = data.append
def extend_callback(ch1_data, _):
    global data_extend
    data_extend(ch1_data)

start_time = time.time()
print("Clearing FIFO and starting data transfer...")
scope.start_capture()
shutdown_event = scope.read_async(extend_callback, blocksize, outstanding_transfers=10,raw=True)
while time.time() - start_time < numseconds:
    scope.poll()
print("Stopping new transfers.")
#scope.stop_capture()
shutdown_event.set()
time.sleep(1)
scope.stop_capture()
scope.close_handle()

total = sum(len(block) for block in data)

filename = "test.wav"
print("Writing out data from scope to {}".format(filename))
with open(filename, "wb") as wf:
    wf.write(b"RIFF")
    wf.write(pack("<L", 44 + total - 8))
    wf.write(b"WAVE")
    wf.write(b"fmt \x10\x00\x00\x00\x01\x00\x01\x00")
    wf.write(pack("<L", samplerate))
    wf.write(pack("<L", samplerate))
    wf.write(b"\x01\x00\x08\x00")
    wf.write(b"data")
    wf.write(pack("<L", total))
    for block in data:
        wf.write(block)
print("Done")
