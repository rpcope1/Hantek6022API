__author__ = 'Robert Cope', 'Jochen Hoenicke'
# This code was used to help execute a side-channel attack on the Trezor Bitcoin wallet.
# See more: http://johoe.mooo.com/trezor-power-analysis/
# Original Author: Jochen Hoenicke

from struct import pack
import sys
import time
from collections import deque

from PyHT6022.LibUsbScope import Oscilloscope

voltagerange = 10        # 1 (5V), 2 (2.6V), 5 or 10
samplerate = 24          # sample rate in MHz or in 10khz
blocksize = 3*1024*24    # must be divisible by 3072
numblocks = 20           # number of blocks to sample
numchannels = 1


scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.flash_firmware_from_hex('../PyHT6022/HantekFirmware/custom/build/firmware.ihx')
scope_channel = 1
print "Setting up scope!"

scope.set_num_channels(numchannels)
# set voltage range
scope.set_ch1_voltage_range(voltagerange)
# set sample rate
scope.set_sample_rate(samplerate)
# we divide by 100 because otherwise audacity lets us not zoom into it
samplerate = samplerate * 1000 * 10 *10
data = []
total = 0

print "Reading data from scope! in ",
for x in range(0, 3):
    print 3-x,"..",
    sys.stdout.flush()
    time.sleep(1)
print "now"

data = deque(maxlen=100*1024*1024)
data_extend = data.extend
def extend_callback(ch1_data, _):
    data_extend(ch1_data)

start_time = time.time()
print "Clearing FIFO and starting data transfer..."
scope.set_interface(1); # choose ISO
scope.clear_fifo()
shutdown_event = scope.read_async(extend_callback, blocksize, outstanding_iso_transfers=5,raw=True)
while time.time() - start_time < 2:
    time.sleep(0.01)
print "Stopping new transfers."
shutdown_event.set()
print "Snooze 5"
time.sleep(5)

#for x in range(0, numblocks):
#    data.append(scope.read_data(blocksize, raw=True, clear_fifo=False)[scope_channel-1])
scope.close_handle()
rawdata = ''.join(data)
total = len(rawdata)

filename = "test.wav"
print "Writing out data from scope to {}".format(filename)
with open(filename, "wb") as wf:
    wf.write("RIFF")
    wf.write(pack("<L", 44 + total - 8))
    wf.write("WAVE")
    wf.write("fmt \x10\x00\x00\x00\x01\x00\x01\x00")
    wf.write(pack("<L", samplerate))
    wf.write(pack("<L", samplerate))
    wf.write("\x01\x00\x08\x00")
    wf.write("data")
    wf.write(pack("<L", total))
    wf.write(rawdata)
print "Done"
