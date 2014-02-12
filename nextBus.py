import urllib.request
import json
from datetime import datetime
#from pprint import pprint

class nextBus(object):

    def getNextBus(self):
        # get current time
        time = datetime.now().time().strftime("%H:%M")

        # build url
        url = "http://online.fahrplan.zvv.ch//bin/stboard.exe/dn?L=vs_widgets&input=Oberengstringen,%%20Eggb%%C3BChl!&dirInput=Z%%C3%%BCrich,%%20Frankental&boardType=dep&time=%s&productsFilter=01001111110&additionalTime=0&disableEquivs=false&maxJourneys=2&start=yes&selectDate=today&monitor=1&requestType=0&timeFormat=cd&view=preview" % time
        timetableData = urllib.request.urlopen(url)

        timetableDataString = timetableData.read().decode(encoding='UTF-8')

        # truncate string
        timetableDataStringTrunc = timetableDataString[14:]
        data = json.loads(timetableDataStringTrunc)

        #pprint(data)
    
        timeToNextBus=list()
        busNr=list()
        busTo=list()
        delay=list()
        for i in range(0,2):
            timeToNextBus.append(data['journey'][i]['countdown_val'])
            busNr.append(data['journey'][i]['pr'])
            busTo.append(data['journey'][i]['st'])
            delay.append(data['journey'][i]['rt']['dlm'])
            #print(busNr + " " + busTo + " " + timeToNextBus + " min (Verspätung: " + delay + " min)")
        
        outputDict = {"timeToNextBus":timeToNextBus, "busNr":busNr, "busTo":busTo, "delay":delay}   
        
        return outputDict
        
        