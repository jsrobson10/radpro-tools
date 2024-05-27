
from datetime import datetime
import sys

def format_unixtime(ts: int):
	return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def row_reader(path: str):
	with open(path, "r") as file:
		file.readline()
		while line := file.readline():
			x, y = str(line).split(",")
			yield (int(x), int(y))

def get_logs(path: str, average_secs: int):

	x_last = 0
	step_last = 0
	step_safe = 0
	log: [(int, int)] = []
	window: [int] = []
	window_sum = 0
	window_at = 0

	for x, y in row_reader(path):
		
		step = x - x_last
		error = step - step_last
		step_last = step
		x_last = x

		if error != 0:
			if len(log) > 0:
				yield log, step_safe, len(window)
			log = []
			window = []
			window_sum = 0
			window_at = 0
			continue

		cpm = y / step * 60
		window_len = average_secs / step
		step_safe = step

		if window_len <= 1:
			log.append((x, cpm))
			continue

		if len(window) < window_len:
			window.append(cpm)
			window_sum += cpm
			continue

		window_sum = window_sum - window[window_at] + cpm
		window[window_at] = cpm
		window_at = (window_at + 1) % len(window)
		log.append((x, window_sum / len(window)))

	if len(log) > 0:
		yield log, step, len(window)

def write_logs(path_in: str, average_secs: int, output_dir: str = ".") -> (str, int):
	
	for log, step, window in get_logs(path_in, average_secs):

		path_out = "{}/log_{}_w{}.s{}.csv".format(output_dir, datetime.fromtimestamp(log[0][0]).strftime('%Y.%m.%d_%H.%M.%S'), window, step)
		
		with open(path_out, "w") as file:
			file.write("# Index,DateTime,CPM\n")
			index = 0
			for ts, cpm in log:
				file.write("{},{},{}\n".format(index, format_unixtime(ts), cpm))
				index += 1
		
		yield (path_out, log[0][0], step, window)

if __name__ == "__main__":
	for path, ts, step, window in write_logs(sys.argv[1], int(sys.argv[2]), sys.argv[3]):
		print("Written {}: {} -> step {} s, window {}".format(path, format_unixtime(ts), step, window))

