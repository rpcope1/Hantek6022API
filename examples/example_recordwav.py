__author__ = 'Robert Cope', 'Jochen Hoenicke'
# This code was used to help execute a side-channel attack on the Trezor Bitcoin wallet.
# See more: http://johoe.mooo.com/trezor-power-analysis/
# Original Author: Jochen Hoenicke

from struct import pack
import StringIO
import sys

from PyHT6022.HTSDKScope import Oscilloscope


scope = Oscilloscope()
scope_channel = 1
if not scope.is_attached():
    print("No scope detected! Check connection!")
    sys.exit(1)
print("Setting up scope!")
# TODO: Are all these extra calls for setup needed?
scope.set_voltage_division(100, 200)
scope.set_voltage_division(1, 6)
scope.set_sampling_rate(500)
samplerate = 1000 * 1000
scope.set_sampling_rate(24)
scope.setup_dso_cal_level()
cal_level = scope.get_calibration_data()
scope.set_dso_calibration(cal_level)

data = []
total = 0

print("Reading data from scope!")
for x in range(0, 10):
    print(x)
    data.append(scope.read_data_from_scope(1047550, raw_data=True)[scope_channel-1])
    total += len(data[x])

filename = "test.wav"
print("Writing out data from scope to {}".format(filename))
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
    raw = StringIO.StringIO()
    for x in data:
        for v in x:
            raw.write(pack("<B", v&0xff))
    wf.write(raw.getvalue())
    raw.close()
print("Done")