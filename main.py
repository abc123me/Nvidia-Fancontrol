#!/usr/bin/python3

from nvfan import *
import atexit

#Some default stuff so you can use this script out-of-the-box
defaultFanCurve = [
	(20, 0),
	(30, 10),
	(35, 20),
	(40, 30),
	(45, 40),
	(60, 60),
	(75, 80),
	(80, 100)
]
lastTemp = -1
changeFactor = 2.5

if(__name__ == '__main__'):
	print("\x1b[01;34mTesting fan control\x1b[0m")
	if(not trySetFanControlEnabled(True)):
		print("\x1b[01;31mUnable to enable fan control!\x1b[0m")
		quit(1)
	legacyFanSpeed = shouldUseLegacyFanSpeed()
	if(legacyFanSpeed):
		print("\x1b[01;33mUsing legacy fan speed!\x1b[0m")
	if(not trySetFanSpeed(100, legacy=legacyFanSpeed)):
		print("\x1b[01;31mUnable to set fan speed!\x1b[0m")
		trySetFanControlEnabled(False)
		quit(1)
	print("\x1b[01;32mFan control works\x1b[0m")
	lastTemp = getGpuTemp() + 1
	def shutdownHook():
		print("\x1b[01;33mShutting down!\x1b[0m")
		if(not trySetFanControlEnabled(False)):
			print("\x1b[01;31mUnable to disable fan control\x1b[0m")
		else:
			print("\x1b[01;32mDisabled fan control\x1b[0m")
	atexit.register(shutdownHook)
	while True:
		temp = getGpuTemp()
		if(temp != lastTemp):
			speed = interpFanCurve(defaultFanCurve, temp)
			change = temp - lastTemp
			col = "\x1b[01;31m"
			if(change < 0):
				col = "\x1b[01;34m"
			print(col + "Temperature changed by " + str(change) + " deg. C\x1b[0m")
			estNextTemp = temp
			if(change > 0):
				estNextTemp = temp + change * changeFactor
			print("\x1b[01;33mFan speed thus changed to " + str(speed) + "% ("+ str(temp) + " deg C, " + str(estNextTemp) + " estimated next)\x1b[0m")
			if(not trySetFanSpeed(estNextTemp, legacy=legacyFanSpeed)):
				print("\x1b[01;31mFailed to set fan speed, exiting!\x1b[0m")
				quit(-1)
			lastTemp = temp
		sleep(1)
