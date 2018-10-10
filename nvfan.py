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

if(__name__ == "__main__"):
	print("This is a library, not a program!")
