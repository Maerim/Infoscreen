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
from next_bus import get_next_bus
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
	myAM2302 = AM2302(pin=4)
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
	 	
	 	
	 	# update bus/temp only every n secs
		if 	(datetime.datetime.now() - last_update).seconds >= UPDATE_FREQUENCY_BUS:
			# get bus
			next_bus_dict = get_next_bus()
			
			
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
			
			display_next_buses(myLCD, next_bus_dict)
			
			temp, hum = myAM2302.get_data()
			display_room_climate_data(myLCD, temp, hum)
			log_room_climate_data('/home/pi/Infoscreen/room_climate.log', temp, hum)
			
			
			last_update = datetime.datetime.now()

		# print the running text for the calendar
		currently_displayed_string = running_string_2[running_index:running_index+16]
		myLCD.printString(currently_displayed_string,7)
		if running_index == len(running_string) + 2: #2=3-1, 3= number of characters in separator (' - ')
			running_index = 0
		else:
			running_index += 1

		sleep(0.3)

def display_next_buses(LCD, bus_dict):
	for i in range(len(bus_dict['busNr'])):
		line_to_display = bus_dict['busNr'][i] + ': ' + bus_dict['timeToNextBus'][i] + ' min (' + bus_dict['delay'][i] + ')'
		LCD.printString(line_to_display, i)


def display_room_climate_data(LCD, temp, hum):
	LCD.printString('Temp: ' + str(round(temp,1)) + ' øC',4)
	LCD.printString('Hum:	 ' + str(round(hum,1)) + ' %',5)
	
def log_room_climate_data(file_name, temp, hum):
    file = open(file_name, 'a')
    file.write('%s \t %f \t %f \n' %(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), temp, hum))
    file.close()

if __name__ == "__main__":
	try:
		main()
	finally:
		GPIO.cleanup()
