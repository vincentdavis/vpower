#!/usr/bin/env python
import os, sys
import time
import csv
import win32api

from ant.core import driver, node, event, message
from ant.core.constants import *

from usb.core import find

from PowerMeterTx import PowerMeterTx
from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID
from functions import interp

if getattr(sys, 'frozen', False):
    # If we're running as a pyinstaller bundle
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def convertSB(raw):
    value = int(raw[1]) << 8
    value += int(raw[0])
    return value

class CadenceListener(event.EventCallback):
    lastTime = None
    lastRevolutions = None

    def calcCadence(self, time, revolutions):
        if self.lastTime is None:
            return 0

        if time < self.lastTime:
            time += 65536

        if revolutions < self.lastRevolutions:
            revolutions += 65536

        return (revolutions - self.lastRevolutions) * 1024 * 60 / (time - self.lastTime)

    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            page = msg.payload[1] & 0x7F
            if page != 0:
                return

            eventTime = convertSB(msg.payload[5:7])
            if eventTime == self.lastTime:
                return

            revolutions = convertSB(msg.payload[7:9])

            cadence = self.calcCadence(eventTime, revolutions)
            power = int(interp(xp, yp, cadence))
            power_meter.update(power)

            self.lastTime = eventTime
            self.lastRevolutions = revolutions

antnode = None
cadence_sensor = None
power_meter = None

last_event = 0
last_time = 0
stopped = True

xp = [0]
yp = [0]
cadence_file = '%s/cadence.csv' % SCRIPT_DIR
if os.path.isfile(cadence_file):
    with open(cadence_file, 'r') as fd:
        reader = csv.reader(fd)
        next(reader, None)
        for line in reader:
            xp.append(int(line[0]))
            yp.append(int(line[1]))
else:
    xp.extend([20, 40, 60, 80, 100, 120, 140])
    yp.extend([40, 80, 100, 200, 400, 600, 800])

def on_exit(sig, func=None):
    if cadence_sensor:
        print("Closing cadence sensor")
        cadence_sensor.close()
        cadence_sensor.unassign()
    if power_meter:
        print("Closing power meter")
        power_meter.close()
        power_meter.unassign()
    if antnode:
        print("Stopping ANT node")
        antnode.stop()

win32api.SetConsoleCtrlHandler(on_exit, True)

try:
    devs = find(find_all=True)
    for dev in devs:
        if dev.idVendor == 0x0fcf and dev.idProduct in [0x1008, 0x1009]:
            break
    else:
        print("No ANT device found")
        if getattr(sys, 'frozen', False):
            input()
        sys.exit()

    stick = driver.USB2Driver(log=LOG, debug=DEBUG, idProduct=dev.idProduct)
    antnode = node.Node(stick)
    print("Starting ANT node")
    antnode.start()
    network = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, network)

    print("Starting cadence sensor")
    try:
        cadence_sensor = antnode.getFreeChannel()
        cadence_sensor.assign(network, CHANNEL_TYPE_TWOWAY_RECEIVE)
        cadence_sensor.setID(122, 0, 0)
        cadence_sensor.searchTimeout = TIMEOUT_NEVER
        cadence_sensor.period = 8102
        cadence_sensor.frequency = 57
        cadence_sensor.open()
    except Exception as e:
        print("cadence_sensor error: " + repr(e))
        cadence_sensor = None

    print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
    try:
        power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
        power_meter.open()
    except Exception as e:
        print("power_meter error: " + repr(e))
        power_meter = None

    cadence_listener = CadenceListener()
    antnode.registerEventListener(cadence_listener)

    print("Main wait loop")
    while True:
        try:
            # Workaround for RGT Cycling and GTBikeV
            if not stopped:
                t = int(time.time())
                if t >= last_time + 3:
                    if cadence_listener.lastTime == last_event:
                        # Set power to zero if cadence sensor doesn't update for 3 seconds
                        power_meter.powerData.instantaneousPower = 0
                        stopped = True
                    last_event = cadence_listener.lastTime
                    last_time = t
                # Force an update every second to avoid power drops
                power_meter.update(power_meter.powerData.instantaneousPower)
            elif power_meter.powerData.instantaneousPower:
                stopped = False
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            break

except Exception as e:
    print("Exception: " + repr(e))
    if getattr(sys, 'frozen', False):
        input()
