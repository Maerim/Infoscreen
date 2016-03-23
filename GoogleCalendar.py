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
		ics = urllib.request.urlopen('https://www.google.com/calendar/ical/7p84iccifkcp7h73dn8sch7cr4%40group.calendar.google.com/private-394b7eabc03f98d0c59c94c972516962/basic.ics').read()
		ical = Calendar.from_ical(ics)

		output_string = []
		
		for vevent in ical.subcomponents:
			start = vevent.get('DTSTART').dt # datetime.date object for whole day events (otherwise datetime!), works therefore only for whole day events!
			if vevent.name == "VEVENT" and start >= datetime.now().date():
				title = str(vevent.get('SUMMARY'))
				end = vevent.get('DTEND').dt

				output_string.append(title + ': ' + start.strftime('%d') + '.' + start.strftime('%m') + '.' +  start.strftime('%y'))
			
		return output_string