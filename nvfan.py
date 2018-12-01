from time import sleep
from socket import gethostname
import subprocess, os

_hostName = gethostname()
_verboseExecution = False

#Enables / Disables verbose execution
def setVerboseExecution(en):
	global _verboseExecution
	_verboseExecution = en
#Executes a command and returns a tuple of the following, (exit code, stdout string, stderr string)
def execCmd(cmd, encoding='utf-8'):
	global _verboseExecution
	if _verboseExecution:
		print("execCmd(cmd): %s" % (str(cmd)))
	p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return (int(p.returncode), str(p.stdout.decode(encoding)), str(p.stderr.decode(encoding)))
#Gets the current XDisplay the process is using
def getXDisplay():
	return os.environ['DISPLAY'].split(".")[0]
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
	versionSplit = res[1].split('.')
#Only use major and minor version, ignore build number.
	return float(versionSplit[0] + '.' + versionSplit[1])
#Trys to set a nvidia setting using the nvidia-settings command
#Checks the stdout for a success message
def trySetNvidiaSetting(attrLoc, attrName, val):
	val = str(val)
	attrArg = '[' + attrLoc + ']/' + attrName + '=' + val
	result = execCmd(['nvidia-settings', '-a', attrArg])
	cout = result[1].strip().replace(' ', '')
	display = getXDisplay()
	check = 'Attribute\'' + attrName + '\'(' + _hostName + display + '[' + attrLoc + '])assignedvalue' + val + '.'
	return (cout == check, cout, check, result[2])
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

class FanError(Exception):
	def __init__(self, msg, reason="Unknown"):
		self._msg = msg
		self._reason = reason
		
	def __str__(self):
		return self._msg + ": " + self._reason
class NVFan:
	def __init__(self, gpu, fan):
		self._gpu = gpu
		self._fan = fan
		self._legacy = shouldUseLegacyFanSpeed()
		res = self.controllable()
		if not res[0]:
			raise FanError("Fan not controllable", res[1])
	def isLegacy():
		return self._legacy
	def controllable(self):
		res = trySetFanControlEnabled(True)
		if(not res[0]):
			return (False, "Unable to enable fan control for gpu %i!" % (self._gpu))
		res = trySetFanSpeed(100, legacy=self.isLegacy(), fan=self._fan)
		if(not res[0]):
			return (False, "Unable to set fan speed for gpu %i, fan %i!" % (self._gpu, self._fan))
			trySetFanControlEnabled(False)
		return (True, "OK")

if(__name__ == "__main__"):
	print("This is a library, not a program!")
