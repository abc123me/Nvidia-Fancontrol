#!/usr/bin/python3

from time import sleep
from socket import gethostname
import subprocess

_hostName = gethostname()

def execCmd(cmd, encoding='utf-8'):
	p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return (int(p.returncode), str(p.stdout.decode(encoding)), str(p.stderr.decode(encoding)))

def getGpuTemp(gpu=0):
	res = execCmd(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'])
	if(res[0] == 0):
		return int(res[1])
	else:
		print('Could not get GPU temperature!')
		print('Output: ' + str(res[1]))
		quit()
def trySetNvidiaSetting(attrLoc, attrName, val):
	val = str(val)
	attrArg = '[' + attrLoc + ']/' + attrName + '=' + val
	result = execCmd(['nvidia-settings', '-a', attrArg])
	cout = result[1].strip().replace(' ', '')
	check = 'Attribute\'' + attrName + '\'(' + _hostName + ':0[' + attrLoc + '])assignedvalue' + val + '.'
	return cout == check
def trySetFanControlEnabled(enabled, gpu=0):
	state = '0'
	if(enabled):
		state = '1'
	return trySetNvidiaSetting('gpu:' + str(gpu), 'GPUFanControlState', state)
def trySetFanSpeed(speed, fan=0, legacy=False):
	if(speed > 100):
		speed = 100
	if(speed < 0):
		speed = 0
	attrName = 'GPUTargetFanSpeed'
	if(legacy):
		attrName = 'GPUCurrentFanSpeed'
	return trySetNvidiaSetting('fan:' + str(fan), attrName, str(int(speed)))
#Fan curve is a list fo tuples
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
	if(not trySetFanControlEnabled(True)):
		print("Unable to enable fan control!")
		quit(1)
	if(not trySetFanSpeed(100)):
		print("Unable to set fan speed!")
		trySetFanControlEnabled(False)
		quit(1)
	while True:
		temp = getGpuTemp()
		if(temp != _lastTemp):
			speed = interpFanCurve(_defaultFanCurve, temp)
			change = temp - _lastTemp
			print("Temperature changed by " + str(change) + " deg. C")
			estNextTemp = temp
			if(change > 1):
				estNextTemp = temp + change * _changeFactor
			print("Fan speed thus changed to " + str(speed) + "% ("+ str(temp) + " deg C, " + str(estNextTemp) + " estimated next)")
			if(not trySetFanSpeed(estNextTemp)):
				print("Failed to set fan speed, exiting!")
				quit(-1)
			_lastTemp = temp
		sleep(1)
