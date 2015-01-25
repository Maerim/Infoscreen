#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ===============
# Jethro Hemmann
# Dezemeber 2013
# ===============


import RPi.GPIO as GPIO
from pprint import pprint
from time import sleep
import datetime
import signal # for catching termination signal
import sys


# CATCH SIGTERM AND SIGINT SIGNALS
def signal_term_handler(signal, frame):
	print('Infoscreen exits...')
	GPIO.cleanup()
	sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGINT, signal_term_handler)


# =======================
# CONFIGURATION CONSTANTS
# =======================
BACKLIGHT_NIGHT_START = datetime.time(22,0,0)
BACKLIGHT_NIGHT_END = datetime.time(6,0,0)
BACKLIGHT_NIGHT_VALUE = 10
BACKLIGHT_DAY_VALUE = 200
# =======================

from nextBus import nextBus
from LCD import LCD
from AM2302 import AM2302


def isNight():
	
	time = datetime.datetime.now().time()
	
	if BACKLIGHT_NIGHT_START <= BACKLIGHT_NIGHT_END:
		return BACKLIGHT_NIGHT_START <= time <= BACKLIGHT_NIGHT_END
	else:
		return BACKLIGHT_NIGHT_START <= time or time <= BACKLIGHT_NIGHT_END


def main():
	myLCD = LCD(CS1=17, CS2=4, E=15, RS=14, D0=27, D1=23, D2=24, D3=25, D4=8, D5=11, D6=9, D7=22, PWM=1)
	myNextBus = nextBus()
	myAM2302 = AM2302()


	# set the initial backlight flag
	if isNight():
		backlightNightFlag = 1
		myLCD.setBacklightPWM(BACKLIGHT_NIGHT_VALUE)
	else:
		backlightNightFlag = 0
		myLCD.setBacklightPWM(BACKLIGHT_DAY_VALUE)


	firstRun = 1

	while(True):
	
		if firstRun != 1: # do not sleep during first run
			sleep(30)
	
		# dim backlight if its night
		if isNight():
			if backlightNightFlag == 0:
				backlightNightFlag = 1
				myLCD.setBacklightPWM(BACKLIGHT_NIGHT_VALUE)
		elif backlightNightFlag == 1:
			backlightNightFlag = 0
			myLCD.setBacklightPWM(BACKLIGHT_DAY_VALUE)
	
		# get bus
		nextBusDict = myNextBus.getNextBus()
		temp = myAM2302.getTemp()
		hum = myAM2302.getHumidity()
	
		myLCD.clearScreen()
	
		for i in range(len(nextBusDict['busNr'])):
			myLCD.printString(nextBusDict['busNr'][i] + ': ' +	nextBusDict['timeToNextBus'][i] + ' min (' + nextBusDict['delay'][i] + ')', i)
	
	
		# display temperature
		myLCD.printString('Temp: ' + str(temp) + ' øC',4)
		myLCD.printString('Hum:	 ' + str(hum) + ' %',5)

		
		# display time of last update (for debugging purposes)
		myLCD.printString('Time: ' + datetime.datetime.now().strftime('%H:%M:%S'),7)

		firstRun = 0


if __name__ == "__main__":
	main()
