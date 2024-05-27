
import serial
import time

class DeviceID:

	def __init__(self, res):
		self.hw_id = res[0]
		self.sw_id = res[1]
		self.d_id = res[2]
	
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return "{} : {} : {}".format(self.hw_id, self.sw_id, self.d_id)

class Device:

	def __init__(self, port: int):
		self.d = serial.Serial(port, 115200)
		if not self.d.isOpen():
			raise RuntimeError("Failed to open port")
	
	def close(self):
		self.d.close()

	def query(self, cmd: str):
		return self.query_one(cmd).split(";")

	def query_one(self, cmd: str):
		self.d.write(bytes("{}\n".format(cmd), "utf-8"))
		return str(self.d.readline()[:-1], "utf-8").removeprefix("OK ")

	def getDeviceId(self):
		res = self.query("GET deviceId")
		return DeviceID(res)

	def getBatteryVoltage(self):
		return float(self.query_one("GET deviceBatteryVoltage"))

	def getTime(self):
		return int(self.query_one("GET deviceTime"))

	def setTime(self, ts: int = int(time.time())):
		return self.query_one("SET deviceTime {}".format(ts))

	def getTubeTime(self):
		return int(self.query_one("GET tubeTime"))

	def setTubeTime(self, ts: int):
		return self.query_one("SET tubeTime {}".format(ts))

	def getTubePulseCount(self):
		return int(self.query_one("GET tubePulseCount"))

	def setTubePulseCount(self, count: int):
		return self.query_one("SET tubePulseCount {}".format(count))

	def getTubeRate(self):
		return float(self.query_one("GET tubeRate"))

	def getTubeConversionFactor(self):
		return float(self.query_one("GET tubeConversionFactor"))

	def getTubeDeadTime(self):
		return float(self.query_one("GET tubeDeadTime"))

	def getTubeDeadTimeCompensation(self):
		return float(self.query_one("GET tubeDeadTimeCompensation"))

	def getTubeHVFrequency(self):
		return float(self.query_one("GET tubeHVFrequency"))

	def setTubeHVFrequency(self, value: float):
		return self.query_one("SET tubeHVFrequency {}".format(value))

	def getTubeHVDutyCycle(self):
		return float(self.query_one("GET tubeHVDutyCycle"))

	def setTubeHVDutyCycle(self, value: float):
		return self.query_one("SET tubeHVDutyCycle {}".format(value))

	def readUntil(self, check: bytes) -> (bytearray, bool):
		line = bytearray()
		while True:
			c = self.d.read()
			if len(c) == 0:
				raise RuntimeError("Timeout during read")
			if c == check:
				return (line, False)
			if c == b"\n":
				return (line, True)
			line.append(c[0])

	def getDataLog(self, since: int = 0) -> [(int, int)]:
		self.d.write(bytes("GET datalog {}\n".format(since), "utf-8"))
		if self.readUntil(b";")[1]:
			return []
		running = True
		y_last = 0
		found: [(int, int)] = []
		while running:
			line, found_nl = self.readUntil(b";")
			if found_nl:
				running = False
			row = str(line, "utf-8")
			if len(row) == 0:
				break
			x, y = row.split(",")
			x = int(x)
			y = int(y)
			if y_last > 0:
				found.append((x, y - y_last))
			y_last = y
		return found
	
	def getRandomData(self):
		res = self.query_one("GET randomData")
		if res == "OK":
			return b''
		return bytes.fromhex(res)

