from time import sleep
from socket import gethostname
import subprocess, os
import sys

_hostName = gethostname()
_verboseExecution = False
_emulating = False
_emulatingVersion = 420.0
_minRevSpeed = 20
_ansiEnabled = True

NC = 0
YELLOW = 1
RED = 2
GREEN = 3
BLUE = 4

color_pref = [
	"\x1b[0m",
	"\x1b[01;33m",
	"\x1b[01;31m",
	"\x1b[01;32m",
	"\x1b[01;34m"
]

#Sets the minimum speed
def setMinimumSpeed(m):
	global _minRevSpeed
	if _verboseExecution: print_color(YELLOW, "Minimum speed set to " + m)
	_minRevSpeed = m
def getMimimumSpeed():
	return _minRevSpeed
#Turns off/on emulation
def setEmulation(e, version=420.0):
	global _emulating,_emulatingVersion
	if e: print_color(YELLOW, "Emulation enabled")
	else: print_color(YELLOW, "Emulation disabled")
	_emulating = e
	_emulatingVersion = version
#Prints colored text
def print_color(color, *args, **kwargs):
	if _ansiEnabled: print(color_pref[color] + "".join(map(str,args)) + "\x1b[0m", **kwargs)
	else: print("".join(map(str,args)) + "\x1b[0m", **kwargs)
#Enables / Disables verbose execution
def setVerboseExecution(en):
	global _verboseExecution
	if en: print_color(YELLOW, "Verbose execution enabled!")
	_verboseExecution = en
#Executes a command and returns a tuple of the following, (exit code, stdout string, stderr string)
def execCmd(cmd, encoding='utf-8'):
	if _emulating: return None
	if _verboseExecution: print_color(NC, "execCmd(cmd): %s" % (str(cmd)))
	p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return (int(p.returncode), str(p.stdout.decode(encoding)), str(p.stderr.decode(encoding)))
#Gets the current XDisplay the process is using
def getXDisplay():
	return os.environ['DISPLAY'].split(".")[0]
#Gets the GPU's temperature using 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader'
def getGpuTemp(gpu=0):
	if _emulating:
		from math import sin
		from time import time
		return (30 + 30 * ((1 + sin(time() / 10000)) / 2))
	res = execCmd(['nvidia-smi', '-i', str(gpu), '--query-gpu=temperature.gpu', '--format=csv,noheader'])
	if res[0] == 0: return int(res[1])
	else:
		print_color(NC, 'Could not get GPU temperature!')
		print_color(NC, 'Output: ' + str(res[1]))
		quit()
#Returns the current driver version
def getDriverVersion(gpu=0):
	if _emulating: return _emulatingVersion
	res = execCmd(['nvidia-smi', '-i', str(gpu), '--query-gpu=driver_version', '--format=csv,noheader'])
	versionSplit = res[1].split('.')
	#Only use major and minor version, ignore build number.
	return float(versionSplit[0] + '.' + versionSplit[1])
#Trys to set a nvidia setting using the nvidia-settings command
#Checks the stdout for a success message
def trySetNvidiaSetting(attrLoc, attrName, val):
	if _emulating: return (True, "Emulating", "Emulating", None)
	val = str(val)
	# {DISPLAY}/{attribute name}[{display devices}]={value}
	attrArg = attrName + '[' + attrLoc + ']' + '=' + val
	result = execCmd(['nvidia-settings', '-a', attrArg])
	cout = result[1].strip().replace(' ', '')
	display = getXDisplay()
	check = 'Attribute\'' + attrName + '\'(' + _hostName + display + '[' + attrLoc + '])assignedvalue' + val + '.'
	return (cout == check, cout, check, result[2])
#Enables/Disables fan control of the nvidia card
def trySetFanControlEnabled(enabled, gpu=0):
	state = '1' if enabled else '0'
	return trySetNvidiaSetting('gpu:' + str(gpu), 'GPUFanControlState', state)
#Sets the fan speed of a nvidia card
#The legacy variable can be determined by shouldUseLegacyFanSpeed()
#Read more here https://wiki.archlinux.org/index.php/NVIDIA/Tips_and_tricks#Set_fan_speed_at_login
def trySetFanSpeed(speed, fan=0, legacy=False):
	if speed < _minRevSpeed: speed = _minRevSpeed
	if speed > 100 or speed < 0: raise ValueError("Speed must be between 0 and 100%!")
	attrName = 'GPUTargetFanSpeed'
	if legacy: attrName = 'GPUCurrentFanSpeed'
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
			speed = m * temp + b
			if(speed < 0): speed = 0
			if(speed > 100): speed = 100
			return speed
		last = cur
	return 50

class FanError(Exception):
	def __init__(self, msg, reason="Unknown"):
		self._msg = msg
		self._reason = reason

	def __str__(self):
		return self._msg + ": " + self._reason

if(__name__ == "__main__"):
	print_color(NC, "This is a library, not a program!")
