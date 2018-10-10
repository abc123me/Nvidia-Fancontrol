#!/usr/bin/python3

from time import sleep
from socket import gethostname
import subprocess

_hostName = gethostname()

#Executes a command and returns a tuple of the following, (exit code, stdout string, stderr string)
def execCmd(cmd, encoding='utf-8'):
	p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return (int(p.returncode), str(p.stdout.decode(encoding)), str(p.stderr.decode(encoding)))
#Gets the GPU's temperature using 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'
def getGpuTemp(gpu=0):
	res = execCmd(['nvidia-smi', '-i', str(gpu), '--query-gpu=temperature.gpu', '--format=csv,noheader'])
	if(res[0] == 0):
		return int(res[1])
	else:
		print('Could not get GPU temperature!')
		print('Output: ' + str(res[1]))
		quit()
#Returns the current driver version
def getDriverVersion(gpu=0):
	res = execCmd(['nvidia-smi', '-i', str(gpu), '--query-gpu=driver_version', '--format=csv,noheader'])
	return float(res[1])
#Trys to set a nvidia setting using the nvidia-settings command
#Checks the stdout for a success message
def trySetNvidiaSetting(attrLoc, attrName, val):
	val = str(val)
	attrArg = '[' + attrLoc + ']/' + attrName + '=' + val
	result = execCmd(['nvidia-settings', '-a', attrArg])
	cout = result[1].strip().replace(' ', '')
	check = 'Attribute\'' + attrName + '\'(' + _hostName + ':0[' + attrLoc + '])assignedvalue' + val + '.'
	return cout == check
#Enables/Disables fan control of the nvidia card
def trySetFanControlEnabled(enabled, gpu=0):
	state = '0'
	if(enabled):
		state = '1'
	return trySetNvidiaSetting('gpu:' + str(gpu), 'GPUFanControlState', state)
#Sets the fan speed of a nvidia card
#The legacy variable can be determined by shouldUseLegacyFanSpeed()
#Read more here https://wiki.archlinux.org/index.php/NVIDIA/Tips_and_tricks#Set_fan_speed_at_login
def trySetFanSpeed(speed, fan=0, legacy=False):
	if(speed > 100):
		speed = 100
	if(speed < 0):
		speed = 0
	attrName = 'GPUTargetFanSpeed'
	if(legacy):
		attrName = 'GPUCurrentFanSpeed'
	return trySetNvidiaSetting('fan:' + str(fan), attrName, str(int(speed)))
#Tells you whether or not you should use the legacy method of setting fan speed
#Read more here https://wiki.archlinux.org/index.php/NVIDIA/Tips_and_tricks#Set_fan_speed_at_login
def shouldUseLegacyFanSpeed(gpu=0):
	return getDriverVersion(gpu) <= 349.16
#Fan curve linearly interpolates against a list fo tuples
def interpFanCurve(fanCurve, temp):
	last = (0, 0)
	for i in range(0, len(fanCurve)):
		cur = fanCurve[i]
		tMin = last[0]
		tMax = cur[0]
		if(temp >= tMin and temp <= tMax):
			sMin = last[1]
			sMax = cur[1]
			m = (sMax - sMin) / (tMax - tMin)
			b = sMin - m * tMin
			return m * temp + b
		last = cur
	return 100

#Some default stuff so you can use this script out-of-the-box
_defaultFanCurve = [
	(20, 0),
	(30, 10),
	(35, 20),
	(40, 30),
	(45, 40),
	(60, 60),
	(75, 80),
	(80, 100)
]
_lastTemp = -1
_changeFactor = 2.5

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
	_lastTemp = getGpuTemp() + 1
	while True:
		temp = getGpuTemp()
		if(temp != _lastTemp):
			speed = interpFanCurve(_defaultFanCurve, temp)
			change = temp - _lastTemp
			col = "\x1b[01;31m"
			if(change < 0):
				col = "\x1b[01;34m"
			print(col + "Temperature changed by " + str(change) + " deg. C\x1b[0m")
			estNextTemp = temp
			if(change > 0):
				estNextTemp = temp + change * _changeFactor
			print("\x1b[01;33mFan speed thus changed to " + str(speed) + "% ("+ str(temp) + " deg C, " + str(estNextTemp) + " estimated next)\x1b[0m")
			if(not trySetFanSpeed(estNextTemp, legacy=legacyFanSpeed)):
				print("\x1b[01;31mFailed to set fan speed, exiting!\x1b[0m")
				quit(-1)
			_lastTemp = temp
		sleep(1)
