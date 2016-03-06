import time

import pylab

from PyHT6022.HTSDKScope import Oscilloscope


if __name__ == "__main__":
    scope0 = Oscilloscope(scopeid=0)
    if not scope0.is_attached():
        print("WARNING: Scope not found!")
        exit()
    scope0.set_voltage_division(1, 5)
    print(scope0.set_sampling_rate(26))
    scope0.setup_dso_cal_level()
    pylab.ion()
    length = 1000
    for i in range(10):
        data = scope0.read_data_from_scope(data_points=3000)
        tIndex = data[3].value
        pylab.plot(data[2][:length], data[0][tIndex:tIndex + length])  # , 'r-')
        pylab.draw()
        time.sleep(1)