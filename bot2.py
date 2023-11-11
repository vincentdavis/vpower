
import PySimpleGUI as sg

from PowerMeterTx import PowerMeterTx

from ant.core import driver
from ant.core import node

from usb.core import find  # this is from pyusb
import usb

backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/opt/homebrew/Cellar/libusb/1.0.24/lib/libusb-1.0.0dylib")

f = find(find_all=True)

from config import DEBUG, LOG, NETKEY, POWER_SENSOR_ID

power_meter = None
stick = None
antnode = None

def connect_stick(idVendor=0x0fcf):
    stick = None
    try:
        devs = find(find_all=True, idVendor=idVendor)
        print(devs)
        for dev in devs:
            if dev.idProduct in [0x1008, 0x1009]:
                stick = driver.USB2Driver(log=LOG, debug=DEBUG, idProduct=dev.idProduct, bus=dev.bus, address=dev.address)
                try:
                    stick.open()
                    stick.close()
                except:
                    stick = None
                break # use the first one found
        else:
            # print("No ANT devices available")
            # if getattr(sys, 'frozen', False):
            #     input()
            # sys.exit()
            stick = None
            return stick
    except:
        raise

def start_antnode(stick):
    antnode = node.Node(stick)
    print("Starting ANT node")
    antnode.start()
    key = node.Network(NETKEY, 'N:ANT+')
    antnode.setNetworkKey(0, key)

# print("Starting power meter with ANT+ ID " + repr(POWER_SENSOR_ID))
# try:
#     # Create the power meter object and open it
#     power_meter = PowerMeterTx(antnode, POWER_SENSOR_ID)
#     power_meter.open()
# except Exception as e:
#     print("power_meter error: " + repr(e))
#     power_meter = None

layout = [
    [sg.Text("Cordyceps: a Zombie Fungus Takes Over Ants Bodies to Controls Zwift")],
    [sg.Button("Powermeter off"), sg.Text('off', key='power_status')],
    [sg.Button("Ant Node off"), sg.Text('off', key='ant_status')],
    [sg.Button("Reset stick"), sg.Text('None', key='stick_status')],

    [sg.Slider(range=(6, 172), orientation='h', size=(10, 20), change_submits=True, key='-SLIDER1-', font=('Helvetica 20'))],
    [sg.Text('Last message', key='messages')]
          ]

# Create the window
window = sg.Window("Cordyceps", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "Powermeter on/off":
        if power_meter:
            # print("Closing power meter")
            power_meter.close()
            power_meter.unassign()
            window['power_status'].update("Off")
        else:
            window['power_status'].update("Already off")
    if event == "Ant Node on/off":
        if antnode:
            # print("Stopping ANT node")
            antnode.stop()
            window['ant_status'].update("Off")
        else:
            window['ant_status'].update("Already off")
    # if event == '-SLIDER1-':
    #     print(int(values['-SLIDER1-']))
    if event == "Reset stick":
        if stick:
            window['stick_status'].update("Already Connected")
        else:
            try:
                stick = connect_stick(idVendor=0x0fcf)
                if stick:
                    window['stick_status'].update("Connected")
                else:
                    window['stick_status'].update("Failed")
            except Exception as e:
                window['stick_status'].update(f'Error: {e}')

    if event == sg.WIN_CLOSED:
        break

window.close()
