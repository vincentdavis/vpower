#!/usr/bin/env python
import os, sys
import time
import csv
import win32api

from ant.core import driver
from ant.core import node
from ant.plus.heartrate import *

from usb.core import find

from PowerMeterTx import PowerMeterTx
from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

antnode = None
hr_monitor = None
power_meter = None

xp = [0]
yp = [0]
last = 0
stopped = True

zones_file = '%s/zones.csv' % SCRIPT_DIR
if os.path.isfile(zones_file):
    with open(zones_file, 'r') as fd:
        reader = csv.reader(fd)
        next(reader, None)
        for line in reader:
            xp.append(int(line[0]))
            yp.append(int(line[1]))

def on_exit(sig, func=None):
    if hr_monitor:
        print("Closing heart rate monitor")
        hr_monitor.close()
    if power_meter:
        print("Closing power meter")
        power_meter.close()
        power_meter.unassign()
    if antnode:
        print("Stopping ANT node")
        antnode.stop()

win32api.SetConsoleCtrlHandler(on_exit, True)

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

def heart_rate_data(computed_heartrate, event_time_ms, rr_interval_ms):
    global last
    global stopped
    t = int(time.time())
    if t >= last + 1:
        power = int(interp(xp, yp, computed_heartrate))
        if power:
            if power_meter: power_meter.update(power)
            stopped = False
        elif not stopped:
            if power_meter: power_meter.update(power)
            stopped = True
        last = t

try:
    devs = find(find_all=True)
    for dev in devs:
        if dev.idVendor == 0x0fcf and dev.idProduct in [0x1008, 0x1009]:
            break

    stick = driver.USB2Driver(log=LOG, debug=DEBUG, idProduct=dev.idProduct)
    antnode = node.Node(stick)
    print("Starting ANT node")
    antnode.start()
    network = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, network)

    print("Starting heart rate monitor")
    try:
        # Create the heart rate monitor object and open it
        hr_monitor = HeartRate(antnode, network, {'onHeartRateData': heart_rate_data})
        hr_monitor.open()
    except Exception as e:
        print("hr_monitor error: " + repr(e))
        hr_monitor = None

    print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
    try:
        # Create the power meter object and open it
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print("power_meter error: " + repr(e))
        power_meter = None

    print("Main wait loop")
    while True:
        try:
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            break

except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
