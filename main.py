#!/usr/bin/python3

from nvfan import *
import atexit

# 2 curves to achieve hysteresis
# curve to be used when speed = 0
highFanCurve = [
	(20, 0),
	(30, 0),
	(35, 10),
	(40, 20),
	(45, 30),
	(50, 40),
	(60, 50),
	(70, 70),
	(80, 90),
	(90, 100)
]
# curve to be used when speed > 0
lowFanCurve = [
	(20, 0),
	(30, 0),
	(35, 0),
	(40, 10),
	(45, 20),
	(55, 30),
	(60, 30),
	(70, 50),
	(80, 70)
]

changeFactor = 2.5
changeThreshold = 1 # The amount of change (in celcius) required to loop

def help():
	print("-----------HELP-----------")
	print("-h:         This help menu")
	print("-e:         Emulate fan control")
	print("-v:         Verbose mode")
	print("-u <float>: Set update rate")
	print("-----------HELP-----------")
	quit(0)

if(__name__ == '__main__'):
	import sys
	update_rate = 1
	if "-h" in sys.argv: help()
	if "-e" in sys.argv: setEmulation(True, 420.0)
	if "-v" in sys.argv: setVerboseExecution(True)
	for i in range(0, len(sys.argv) - 1):
		next = sys.argv[i + 1]
		arg = sys.argv[i]
		if arg == '-u':
			update_rate = float(next)
			print_color(BLUE, "Update rate set to %.1fs" % update_rate)
	speed = 0.0
	temp = 0.0
	try:
		print_color(BLUE, "Testing fan control")
		res = trySetFanControlEnabled(True)
		if(not res[0]):
			print_color(RED, "Unable to enable fan control!")
			print_color(RED, "Reason: %s != %s %s" % (res[1], res[2], res[3]));
			quit(1)
		print_color(YELLOW, "Checking legacy")
		legacyFanSpeed = shouldUseLegacyFanSpeed()
		if(legacyFanSpeed):
			print_color(YELLOW, "Using legacy fan speed!")
		res = trySetFanSpeed(50, legacy=legacyFanSpeed)
		if(not res[0]):
			print_color(RED, "Unable to set fan speed!")
			print_color(RED, "Reason: %s != %s % (res[1], res[2])");
			trySetFanControlEnabled(False)
			quit(1)
	except FileNotFoundError:
		print_color(RED, "NVIDIA drivers are not installed, this tool only works with the proprietary NVIDIA drivers")
		quit(1)
	print_color(GREEN, "Fan control works")

	lastTemp = getGpuTemp() + 1

	def shutdownHook():
		print_color(YELLOW, "Shutting down!")
		res = trySetFanControlEnabled(False)
		if(not res[0]):
			print_color(RED, "Unable to disable fan control")
			print_color(RED, "Reason: %s != %s % (res[1], res[2])");
		else:
			print_color(GREEN, "Disabled fan control")
	atexit.register(shutdownHook)
	try:
		while True:
			temp = getGpuTemp()
			if(temp != lastTemp):
				change = temp - lastTemp
				col = RED
				if(change < 0):
					col = BLUE
				print_color(col, "Temperature changed by " + str(change) + " deg. C")
				estNextTemp = temp
				if(change > 0):
					estNextTemp = temp + change * changeFactor
				# add hysteresis
				if (speed > 0):
					funCurve = lowFanCurve
				else:
					funCurve = highFanCurve
				speed = interpFanCurve(funCurve, estNextTemp)
				print_color(YELLOW, "Fan speed thus changed to " + str(speed) + "% (" + str(temp) + " deg C, " + str(estNextTemp) + " estimated next)")
				res = trySetFanSpeed(speed, legacy=legacyFanSpeed)
				if(not res[0]):
					print_color(RED, "Failed to set fan speed, exiting!")
					print_color(RED, "Reason: %s != %s % (res[1], res[2])");
					quit(-1)
				lastTemp = temp
				sleep(update_rate)
	except KeyboardInterrupt:
		print_color(RED, "Exiting now!")
		quit(1)
