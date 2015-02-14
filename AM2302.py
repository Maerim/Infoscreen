import subprocess
import re
import time
import datetime
import os

class AM2302(object):
	
	def __init__(self):
		self.temp = 0.0
		self.hum = 0.0
		self.update()
	
	def update(self):
	
		# Code adapted from Adafruit
		# Run the DHT program to get the humidity and temperature readings!

		output = subprocess.check_output([os.path.dirname(os.path.realpath(__file__)) + "/Adafruit_DHT", "2302", "4"]);
		matches = re.search(b"Temp =\s+([0-9.]+)", output)
		if (not matches):
			#time.sleep(3)
			#self.update() # retry the update and exit the function
			return
		temp = float(matches.group(1))

		# search for humidity printout
		matches = re.search(b"Hum =\s+([0-9.]+)", output)
		if (not matches):
			#time.sleep(3)
			#self.update()
			return
		humidity = float(matches.group(1))
		
		self.temp = temp
		self.hum = humidity
		
	def getTemp(self):
		self.update()
		return self.temp
	
	def getHumidity(self):
		self.update()
		return self.hum
