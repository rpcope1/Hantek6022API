__author__ = 'Robert Cope', 'Jochen Hoenicke'
# This code was used to help execute a side-channel attack on the Trezor Bitcoin wallet.
# See more: http://johoe.mooo.com/trezor-power-analysis/
# Original Author: Jochen Hoenicke

from struct import pack
import sys
import time

from PyHT6022.LibUsbScope import Oscilloscope

voltagerange = 10       # 1 (5V), 2 (2.6V), 5 or 10
samplerate = 16         # sample rate in MHz or in 10khz
blocksize = 8*1000*1000 # set to <  8 000 000 for two channels
                        #        < 16 000 000 for one channel
                        # must be divisible by 512
numblocks = 1           # number of blocks to sample
numchannels = 1


scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.flash_firmware()
scope_channel = 1
print "Setting up scope!"

scope.set_num_channels(numchannels)
# set voltage range
scope.set_ch1_voltage_range(voltagerange)
# set sample rate
scope.set_sample_rate(samplerate)
# we divide by 100 because otherwise audacity lets us not zoom into it
samplerate = samplerate * 1000 * 10
data = []
total = 0

print "Reading data from scope! in ",
for x in range(0, 3):
    print 3-x,"..",
    sys.stdout.flush()
    time.sleep(1)
print "now"
for x in range(0, numblocks):
    data.append(scope.read_data(blocksize, raw=True, clear_fifo=False)[scope_channel-1])
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
