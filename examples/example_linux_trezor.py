__author__ = 'Robert Cope', 'Jochen Hoenicke'
# This code was used to help execute a side-channel attack on the Trezor Bitcoin wallet.
# See more: http://johoe.mooo.com/trezor-power-analysis/
# Original Author: Jochen Hoenicke

from struct import pack
import sys

from PyHT6022.LibUsbScope import Oscilloscope


scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope_channel = 1
print "Setting up scope!"
# set voltage range
scope.set_ch1_voltage_range(10)
# 16 MHz sample rate
scope.set_sample_rate(16)
# we divide by 10 because otherwise audacity lets us not zoom into it
samplerate = 16 * 1000 * 1000 / 10
data = []
total = 0

print "Reading data from scope!"
for x in range(0, 20):
    print x
    data.append(scope.read_data(8*1000*1000, raw=True)[scope_channel-1])
    total += len(data[x])
scope.close_handle()

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
    for x in data:
        wf.write(x)
print "Done"
