# -*- coding: utf-8 -*-

# ===============
# Jethro Hemmann
# March 2016
# ===============

from icalendar import Calendar
import urllib.request
from datetime import datetime
	
class GoogleCalendar():

	def get_events(self):
		try:
			ics = urllib.request.urlopen('https://calendar.google.com/calendar/ical/6i14lijqhiokqa5jo7uore2ies%40group.calendar.google.com/private-f834ecc877180ed06c3e1fb4a26327f8/basic.ics').read()
			ical = Calendar.from_ical(ics)

			output_list = []
		
			for vevent in ical.subcomponents:
				start = vevent.get('DTSTART').dt # datetime.date object for whole day events (otherwise datetime!), works therefore only for whole day events!
				if vevent.name == "VEVENT" and start >= datetime.now().date(): # return only events in the future
					title = str(vevent.get('SUMMARY'))
					#end = vevent.get('DTEND').dt #not needed, since only whole day events are considered atm
					output_list.append((start, title))
		

			output_list.sort()
			output_string = [item[1] + ': ' + item[0].strftime('%d') + '.' + item[0].strftime('%m') + '.' + item[0].strftime('%y') for item in output_list] 
		
		except:
			output_string = 'Error'
		
		return output_string