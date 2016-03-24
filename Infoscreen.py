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

# own imports
from nextBus import nextBus
from LCD import LCD
from AM2302 import AM2302
from GoogleCalendar import GoogleCalendar


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
UPDATE_FREQUENCY_BUS = 15 # update bus/temp every n seconds

BACKLIGHT_NIGHT_START = datetime.time(22,0,0)
BACKLIGHT_NIGHT_END = datetime.time(6,0,0)
BACKLIGHT_NIGHT_VALUE = 10
BACKLIGHT_DAY_VALUE = 200
# =======================


def isNight():
	
	time = datetime.datetime.now().time()
	
	if BACKLIGHT_NIGHT_START <= BACKLIGHT_NIGHT_END:
		return BACKLIGHT_NIGHT_START <= time <= BACKLIGHT_NIGHT_END
	else:
		return BACKLIGHT_NIGHT_START <= time or time <= BACKLIGHT_NIGHT_END


def main():

	# create objects
	myLCD = LCD(CS1=17, CS2=7, E=15, RS=14, D0=27, D1=23, D2=24, D3=25, D4=8, D5=11, D6=9, D7=22, PWM=1) #PWM pin number is wiringPi numbering!
	myNextBus = nextBus()
	myAM2302 = AM2302()
	myCalendar = GoogleCalendar()

	# set the initial backlight flag
	if isNight():
		backlightNightFlag = 1
		myLCD.setBacklightPWM(BACKLIGHT_NIGHT_VALUE)
	else:
		backlightNightFlag = 0
		myLCD.setBacklightPWM(BACKLIGHT_DAY_VALUE)

	

	last_update = datetime.datetime.now() - datetime.timedelta(seconds=UPDATE_FREQUENCY_BUS)
	while(True):
	
		# dim backlight if its night
		if isNight():
			if backlightNightFlag == 0:
				backlightNightFlag = 1
				myLCD.setBacklightPWM(BACKLIGHT_NIGHT_VALUE)
		elif backlightNightFlag == 1:
			backlightNightFlag = 0
			myLCD.setBacklightPWM(BACKLIGHT_DAY_VALUE)
	 	
	 	
	 	# update bus/temp only every 30 s
		if 	(datetime.datetime.now() - last_update).seconds >= UPDATE_FREQUENCY_BUS:
			# get bus
			nextBusDict = myNextBus.getNextBus()
			# get temp and humidity
			temp = myAM2302.getTemp()
			hum = myAM2302.getHumidity()
			
			# update calendar data
			events = myCalendar.get_events()
			if len(events) > 1: # only display next 2 events
				running_string = events[0] + ' - ' + events[1]
			elif len(events) == 0: 
				running_string = 'No events scheduled'
			else: # only 1 event
				running_string = events[0]
			running_string_2 = running_string + ' - ' + running_string # double string to make it easier for running it over the screen
			running_index = 0
			
			# display bus
			for i in range(len(nextBusDict['busNr'])):
				myLCD.printString(nextBusDict['busNr'][i] + ': ' +	nextBusDict['timeToNextBus'][i] + ' min (' + nextBusDict['delay'][i] + ')', i)
			# display temperature
			myLCD.printString('Temp: ' + str(temp) + ' øC',4)
			myLCD.printString('Hum:	 ' + str(hum) + ' %',5)
			
			last_update = datetime.datetime.now()

		# print the running text for the calendar
		currently_displayed_string = running_string_2[running_index:running_index+16]
		myLCD.printString(currently_displayed_string,7)
		if running_index == len(running_string) + 2: #2=3-1, 3= number of characters in separator (' - ')
			running_index = 0
		else:
			running_index += 1

		sleep(0.3)

if __name__ == "__main__":
	main()
