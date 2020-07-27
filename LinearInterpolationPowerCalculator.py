import os, sys
import csv
from AbstractPowerCalculator import AbstractPowerCalculator

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def interp(x_arr, y_arr, x):
    for i, xi in enumerate(x_arr):
        if xi >= x:
            break
    else:
        return y_arr[-1]

    x_min = x_arr[i - 1]
    y_min = y_arr[i - 1]
    y_max = y_arr[i]
    factor = (x - x_min) / (xi - x_min)
    return y_min + (y_max - y_min) * factor

class LinearInterpolationPowerCalculator(AbstractPowerCalculator):
    def __init__(self):
        super(LinearInterpolationPowerCalculator, self).__init__()
        self.wheel_circumference = 2.105  # default value - can be overridden in config.py

    xp = [0]
    yp = [0]
    curve_file = '%s/curve.csv' % SCRIPT_DIR
    if os.path.isfile(curve_file):
        with open(curve_file, 'r') as fd:
            reader = csv.reader(fd)
            next(reader, None)
            for line in reader:
                xp.append(int(line[0]))
                yp.append(int(line[1]))

    def power_from_speed(self, revs_per_sec):
        kms_per_rev = self.wheel_circumference / 1000.0
        speed = revs_per_sec * 3600 * kms_per_rev
        power = int(interp(self.xp, self.yp, speed))
        return power

    def set_wheel_circumference(self, circumference):
        self.wheel_circumference = circumference
