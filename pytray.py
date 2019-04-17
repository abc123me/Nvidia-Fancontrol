#!/usr/bin/python3


# This code is an example for a tutorial on Ubuntu Unity/Gnome AppIndicators:
# http://candidtim.github.io/appindicator/2014/09/13/ubuntu-appindicator-step-by-step.html

import os
import signal
import json

from urllib import request
from urllib.error import URLError
from urllib.request import urlopen

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import GLib as glib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

import subprocess
import os

APPINDICATOR_ID = 'myappindicator'

def make_indicator():
	return appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('sample_icon.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)

retry = 0
proc = subprocess.Popen(["./main.py", "2>/dev/null"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
fdin = proc.stdout.fileno()
fdout = proc.stdin.fileno()

def make_proc():
	global proc
	global fdin
	global fdout
	if proc.poll():
		# dead
		proc = subprocess.Popen(["./main.py", "2>/dev/null"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
		fdin = proc.stdout.fileno()
		fdout = proc.stdin.fileno()

def request_temp_speed():
	global fdin
	global fdout
	temp = None
	speed = None
	try:
		# write whatever to pipe
		os.write(fdout, b'1')
		temp = os.read(fdin, 4)
		speed = os.read(fdin, 4)
	except:
		pass
	return temp, speed

def lbl_change(ind):
	global retry
	temp, speed = request_temp_speed()
	if not temp or not speed:
		if retry != 0:
			ind.set_label('FAIL', '8.8')
			# return false - timer stops
			return False
		else:
			# restart nvfan
			try: make_proc()
			except: return False
			# schedule one retry
			retry = 1
			return True
	temp_str = str(int.from_bytes(temp, 'little'))
	speed_str = str(int.from_bytes(speed, 'little'))
	label = str("T: " + temp_str + ", S: " + speed_str)
	ind.set_label(label, '8.8')
	retry = 0
	return True

def main():
	indicator = make_indicator()
	indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
	indicator.set_menu(build_menu())
	indicator.set_label('--', '8.8')
	notify.init(APPINDICATOR_ID)
	# start periodic attempt to set Label
	glib.timeout_add(2000, lbl_change, indicator)
	gtk.main()

def build_menu():
	menu = gtk.Menu()
	item_joke = gtk.MenuItem('Joke')
	item_joke.connect('activate', joke)
	menu.append(item_joke)
	item_quit = gtk.MenuItem('Quit')
	item_quit.connect('activate', quit)
	menu.append(item_quit)
	menu.show_all()
	return menu

def fetch_joke():
	with urlopen('http://api.icndb.com/jokes/random?limitTo=[nerdy]') as req:
		msg = req.read();
		msg = msg.decode('utf-8')
		joke = json.loads(msg)['value']['joke']
	return joke

def joke(_):
	notify.Notification.new("<b>Joke</b>", fetch_joke(), None).show()

def quit(_):
	notify.uninit()
	gtk.main_quit()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	main()
