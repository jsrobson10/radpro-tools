
from device import Device
import time
import sys

device = Device(sys.argv[1])

print(device.getDeviceId())
print(device.query_one(" ".join(sys.argv[2:])))

