#!/usr/bin/env python
import sys
import time
import platform
import random
import tkinter as tk

from ant.core import driver
from ant.core import node

from usb.core import find

from PowerMeterTx import PowerMeterTx
from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID

antnode = None
power_meter = None

def stop_ant():
    if power_meter:
        print("Closing power meter")
        power_meter.close()
        power_meter.unassign()
    if antnode:
        print("Stopping ANT node")
        antnode.stop()

pywin32 = False
if platform.system() == 'Windows':
    def on_exit(sig, func=None):
        stop_ant()
    try:
        import win32api
        win32api.SetConsoleCtrlHandler(on_exit, True)
        pywin32 = True
    except ImportError:
        print("Warning: pywin32 is not installed, use Ctrl+C to stop")

def disable_event():
    pass

try:
    devs = find(find_all=True, idVendor=0x0fcf)
    for dev in devs:
        if dev.idProduct in [0x1008, 0x1009]:
            stick = driver.USB2Driver(log=LOG, debug=DEBUG, idProduct=dev.idProduct, bus=dev.bus, address=dev.address)
            try:
                stick.open()
            except:
                continue
            stick.close()
            break
    else:
        print("No ANT devices available")
        if getattr(sys, 'frozen', False):
            input()
        sys.exit()

    antnode = node.Node(stick)
    print("Starting ANT node")
    antnode.start()
    key = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, key)

    print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
    try:
        # Create the power meter object and open it
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print("power_meter error: " + repr(e))
        power_meter = None


# Py Simple Gui
    layout = [
        [sg.Text("Cordyceps: a Zombie Fungus Takes Over Ants Bodies to Controls Zwift")],
        [sg.Slider(range=(5, 1000), orientation='h', size=(10, 20), change_submits=True, key='-SLIDER1-', font=('Helvetica 20'))],
            ]
    # Create the window
    window = sg.Window("Cordyceps", layout)

    last = 0
    stopped = True

    print("Main wait loop")
    power = None
    # Create an event loop
    while True:
        event, values = window.read()
        try:
            t = int(time.time())
            if t >= last + 1:
                adj = random.randint(a=-5, b=5)
                if not power:
                    power = 5
                if event == '-SLIDER1-':
                    power = int(values['-SLIDER1-'])
                if power:
                    power_meter.update(power)
                    stopped = False
                elif not stopped:
                    power_meter.update(power)
                    stopped = True
                last = t
        except (KeyboardInterrupt, SystemExit):
            break
        if event == sg.WIN_CLOSED:
            break

    window.close()

except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
finally:
    if not pywin32:
        stop_ant()
