#!/usr/bin/env python
import time
import win32api
import Tkinter as tk

from ant.core import driver
from ant.core import node

from PowerMeterTx import PowerMeterTx
from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID

antnode = None
power_meter = None

def close_all():
    if power_meter:
        print "Closing power meter"
        power_meter.close()
        power_meter.unassign()
    if antnode:
        print "Stopping ANT node"
        antnode.stop()

def on_exit(sig, func=None):
    close_all()

win32api.SetConsoleCtrlHandler(on_exit, True)

try:
    stick = driver.USB2Driver(None, log=LOG, debug=DEBUG)
    antnode = node.Node(stick)
    print "Starting ANT node"
    antnode.start()
    key = node.NetworkKey('N:ANT+', NETKEY)
    antnode.setNetworkKey(0, key)

    print "Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID)
    try:
        # Create the power meter object and open it
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print "power_meter error: " + e.message
        power_meter = None

    master = tk.Tk()
    master.title("Bot")
    master.geometry("200x50")
    master.call('wm', 'attributes', '.', '-topmost', '1')
    w = tk.Scale(master, from_=0, to=1000, length=200, orient=tk.HORIZONTAL)
    w.pack()

    t = 0
    last = 0
    power = 0

    print "Main wait loop"
    while True:
        power = w.get()
        t = int(time.time())
        if power and t >= last + 1:
            power_meter.update(power)
        last = t
        master.update_idletasks()
        master.update()

except:
    pass
finally:
    close_all()
