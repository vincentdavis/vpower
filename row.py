#!/usr/bin/env python
import sys
import time
import platform

from ant.core import driver
from ant.core import node

from usb.core import find

from pyrow import pyrow

from PowerMeterTx import PowerMeterTx
from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID

antnode = None
power_meter = None

last = 0
stopped = True

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

try:
    # Connecting to erg
    ergs = list(pyrow.find())
    if len(ergs) == 0:
        print("No ergs found")
        if getattr(sys, 'frozen', False):
            input()
        sys.exit()

    erg = pyrow.pyrow(ergs[0])
    print("Connected to erg")

    # Starting ANT node
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
    network = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, network)

    print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
    try:
        # Create the power meter object and open it
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print("power_meter error: " + repr(e))
        power_meter = None

    while True:
        try:
            workout = erg.get_workout()
            print("Waiting for workout to start")
            while workout['state'] == 0:
                time.sleep(1)
                workout = erg.get_workout()
            print("Workout has begun")

            # Loop until workout ends
            while workout['state'] == 1:

                forceplot = erg.get_force_plot()

                # Loop while waiting for drive
                while forceplot['strokestate'] != 2 and workout['state'] == 1:
                    time.sleep(.5)
                    forceplot = erg.get_force_plot()
                    workout = erg.get_workout()
                    if not stopped:
                        # Workaround for RGT keeping the last power value
                        if int(time.time()) >= last + 4:
                            # Send zero power message on 4 seconds timeout
                            power_meter.update(0, 0)
                            stopped = True
                        else:
                            monitor = erg.get_monitor()
                            power_meter.update(monitor['power'], monitor['spm'])

                # Loop during drive
                while forceplot['strokestate'] == 2:
                    time.sleep(.1)
                    forceplot = erg.get_force_plot()

                last = int(time.time())
                stopped = False

                # Get workout conditions
                workout = erg.get_workout()

            print("Workout has ended")

        except (KeyboardInterrupt, SystemExit):
            break

except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
finally:
    if not pywin32:
        stop_ant()
