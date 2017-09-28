#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import subprocess
import json
import os
import socket
from requests import *
import time
#import webbrowser
#from urllib import urlencode

timestamps = {}

TIMESTAMPS_FILE = r'C:\LucidEye\timestamps.txt'

ADB_PATH = sys.argv[1]

def runAdbCommand(pathCmd):
	process = subprocess.Popen(pathCmd, executable=ADB_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	res = process.communicate()[0]
	return res

msg = "http://qa-srv/cgi-bin/mobile/lucideye.cgi?action=found" 


DeviceID = runAdbCommand(['adb', 'devices'])

#findStr = 'Device ID = '
temp = '\''
#print

s = 'unauthorized'
if s in DeviceID:
	exit(1)

errorMsg = 'No such file or directory'
	
macList = runAdbCommand(['adb', 'shell', 'cat', '/sys/class/net/wlan0/address']).strip()
#print macList

if macList == []:
	exit(1)
elif errorMsg in macList:
	macList = runAdbCommand(['adb', 'devices']).strip()
	macList = macList.split('d', 1)[1]
	macList = macList.split('d', 1)[1]
	macList = macList.rsplit('d', 1)[0]
	macList = macList.strip()
msg = msg + '&macs='
MACS = ''
#print msg

for mac in macList:
	msg = msg + mac
hostName = socket.gethostname()
hostName = bytes(hostName.strip()) #, 'UTF-8')
msg = msg + bytes('&hostname=') + hostName #, 'UTF-8')
data = msg
data = data.split("&macs=", 1)[1]
data = data.rsplit("&hostname=", 1)[0]
my_mac_identifier = macList
#print data

def getMyMacIdentifier():
	return my_mac_identifier


# FIXME change this to get time from the server
def getTimestampNow():
	timestamp = int(time.time())
	return timestamp

def shouldUpdateServerAboutConnection(mac):
	delta_s = 10  # update threshold
	global timestamps
	
	if not os.path.exists(TIMESTAMPS_FILE):
		return True
	
	with open(TIMESTAMPS_FILE) as f:
		timestamps = json.load(f)
	
	if mac not in timestamps:
		timestamps[mac] = getTimestampNow()
		return True
	else:
		ts = timestamps[mac]
		now = getTimestampNow()
		
		if now - ts > delta_s:
			return True
		else:
			return False

def updateServer(my_mac_id):
	final = msg + "&device_id=" + my_mac_id
	if my_mac_id == '':
		exit()
	else:
		r = get(final)
#		print final

def updateDeviceTimestamp(mac_id):
	timestamps[mac_id] = getTimestampNow()
	
def saveTimestampData():
	json.dump(timestamps, open(TIMESTAMPS_FILE, "w"))
	
	
my_mac_id = getMyMacIdentifier()

if shouldUpdateServerAboutConnection(my_mac_id):
	updateDeviceTimestamp(my_mac_id)
	updateServer(my_mac_id)
	saveTimestampData()
#	print 'UPDATED!'  # for debugging
else:
#	print 'NOT UPDATED!'  # for debugging
	pass


