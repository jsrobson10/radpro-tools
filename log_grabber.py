
from device import Device
import log_extractor
import json
import sys

meta = {"at": 0}
device = Device(sys.argv[1])

print("Found: {}".format(device.getDeviceId()))

try:
	with open("meta.json", "r") as file:
		meta = json.load(file)

except IOError:
	pass

at = meta["at"]
file_log = None

print("Reading from {}".format(log_extractor.format_unixtime(at)))

if at == 0:
	file_log = open("log.csv", "w")
	file_log.write("Timestamp,Clicks\n")
else:
	file_log = open("log.csv", "a")

clicks_total = 0

for timestamp, clicks in device.getDataLog(at):
	file_log.write("{},{}\n".format(timestamp, clicks))
	at = timestamp + 1 # only continue after this timestamp
	clicks_total += clicks

device.close()
file_log.close()
meta = {"at": at}

with open("meta.json", "w") as file:
	json.dump(meta, file)

print("Recorded {} clicks".format(clicks_total))

