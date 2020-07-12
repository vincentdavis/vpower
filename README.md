# ANT+ Virtual Power Meter

## Overview

This project implements "virtual power" for bicycle turbo trainers where the trainer or the attached bike has an ANT+ 
speed sensor. The calculated power is broadcasted as such on ANT+ so that any head unit or app will see it as a power
meter. This version (forked from vpower by Darren Hague) is adapted to run on Windows. Even if the receiver app runs
on the same computer, you will need two ANT+ sticks, because one device can't be used by two apps simultaneously.

Currently supported trainers:
* [Bike Technologies Advanced Training System (BT-ATS)](http://www.biketechnologies.com/bt-advanced-training-system/)
* [CycleOps Fluid2](https://www.cycleops.com/product/fluid2)
* [Generic Fluid](http://www.powercurvesensor.com/cycling-trainer-power-curves/)
* [Generic Magnetic (medium resistance)](http://www.powercurvesensor.com/cycling-trainer-power-curves/)
* [Kurt Kinetic range of fluid trainers](https://kurtkinetic.com/products/trainers/)
* [Tacx Blue Motion](https://tacx.com/product/blue-motion/)

It is easy to add a new trainer - just subclass `AbstractPowerCalculator` and implement the method `power_from_speed(revs_per_sec)`.
If your trainer is not there, please add it and submit a pull request.

## Running on Windows

* Download the [standalone executable](https://github.com/oldnapalm/vpower/releases/tag/v0.1)

* Configure speed sensor, power calculator and wheel circumference in **vpower.cfg**

* Install the libusb-win32 driver for the ANT+ device, it can be easily done using [Zadig](https://zadig.akeo.ie/)
  * Options - List All Devices
  * Select ANT+ stick
  * Select libusb-win32 driver and click Replace Driver

Supported devices:
* [ANTUSB2 Stick](http://www.thisisant.com/developer/components/antusb2/) (0fcf:1008: Dynastream Innovations, Inc.)
* [ANTUSB-m Stick](http://www.thisisant.com/developer/components/antusb-m/) (0fcf:1009: Dynastream Innovations, Inc.)

### Running from source

* Install [Python 2](https://www.python.org/downloads/) if not already installed
* Clone or download [python-ant](https://github.com/oldnapalm/python-ant) repo
* In a Command Prompt within python-ant repo directory, run ``C:\Python27\python.exe setup.py install``
* Clone or download this repo
* In a Command Prompt within the repo directory, run ``C:\Python27\python.exe vpower.py`` (or open vpower.py directly
from Windows Explorer if .py file type is associated with python.exe)

## Troubleshooting

* USBError: could not claim interface
  * Make sure the device is not in use by other app
  * Unplug and replug the ANT+ stick
* Stuck on "Starting ANT node"
  * Unplug and replug the ANT+ stick

Original [README.md](https://github.com/dhague/vpower/blob/master/README.md)
