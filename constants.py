import subprocess

SPEED_DEVICE_TYPE = 0x7B
CADENCE_DEVICE_TYPE = 0x7A
SPEED_CADENCE_DEVICE_TYPE = 0x79
POWER_DEVICE_TYPE = 0x0B


# Get the serial number of CPU
def getserial():
    # Extract serial from wmic command
    cpuserial = "0000000000000000"
    try:
        cpuserial = subprocess.check_output('wmic cpu get ProcessorId').split('\n')[1].strip()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial
