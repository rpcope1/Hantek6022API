__author__ = 'Robert Cope'

# This script is a hack to get samples from the scope and dump them to a file

from PyHT6022.LibUsbScope import Oscilloscope
import time 
import atexit

samplerate = 4
voltage_range = 2
numchannels = 1
blocksize = 6*1024      # should be divisible by 6*1024
alternative = 1         # choose ISO 3072 bytes per 125 us

@atexit.register
def close():
  time.sleep(2)
  scope.stop_capture()
  scope.close_handle()

data = []
data_extend = data.append
def extend_callback(ch1_data, _):
  data_extend(ch1_data)

f = open("test.out", "wb")
scope = Oscilloscope()
scope.setup()
scope.open_handle()
scope.set_interface(alternative);
scope.set_num_channels(numchannels)
scope.set_ch1_voltage_range(voltage_range)
scope.set_sample_rate(samplerate)
scope.start_capture()

while True:
 scope.read_async(extend_callback, blocksize, outstanding_transfers=1,raw=True)
 for block in data:
  f.write(block)

