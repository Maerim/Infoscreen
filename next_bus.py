# -*- coding: utf-8 -*-


def _read_data_from_zvv():

	import urllib.request
	import json
	from datetime import datetime
	
	current_time = datetime.now().time().strftime("%H:%M")
	url = "http://online.fahrplan.zvv.ch/bin/stboard.exe/dn?L=vs_widgets&input=Oberengstringen,%%20Eggb%%C3BChl!&dirInput=Z%%C3%%BCrich,%%20Frankental&boardType=dep&time=%s&productsFilter=01001111110&additionalTime=0&disableEquivs=false&maxJourneys=2&start=yes&selectDate=today&monitor=1&requestType=0&timeFormat=cd&view=preview" % current_time
		
	try: 
		timetable_data = urllib.request.urlopen(url).read()
		
		# enable logging
		#print(timetable_data, flush=True)
	
		timetable_data_string = timetable_data.decode(encoding='UTF-8')
	except:
		return None
		

	timetable_data_string_truncated = timetable_data_string[14:]
	data = json.loads(timetable_data_string_truncated)
	
	return data

def get_next_bus():

	data = _read_data_from_zvv()

	if data == None:
		empty_data = {"timeToNextBus":'-', "busNr":'-', "busTo":'-', "delay":'-'}
		return 	empty_data


	timeToNextBus=list()
	busNr=list()
	busTo=list()
	delay=list()
	
	nr_buses_to_use = min(2,len(data['journey'])) # trying to catch cases where ZVV returns less than 2 buses
	
	for i in range(nr_buses_to_use):
		timeToNextBus.append(data['journey'][i]['countdown_val'])
		busNr.append(data['journey'][i]['pr'])
		busTo.append(data['journey'][i]['st'])
		
		# sometimes the delay (rt) from ZVV will just output false
		if data['journey'][i]['rt'] == False:
			delay.append('0')
		else:
			delay.append(data['journey'][i]['rt']['dlm'])
			
		#print(busNr + " " + busTo + " " + timeToNextBus + " min (Verspätung: " + delay + " min)")
	
	outputDict = {"timeToNextBus":timeToNextBus, "busNr":busNr, "busTo":busTo, "delay":delay}	
	
	return outputDict
