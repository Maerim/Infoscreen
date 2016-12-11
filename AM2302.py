import Adafruit_DHT

class AM2302:
	
	def __init__(self, pin):
		self.temp = 0.0
		self.hum = 0.0
		self.pin = pin
		self.update()
	
	def update(self):
		humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, self.pin)
		
		if humidity == None:
			humidity = 0.0
		if temperature == None:
			temperature = 0.0
		
		self.temp = round(temperature,1)
		self.hum = round(humidity,1)
		
	def getTemp(self):
		self.update()
		return self.temp
	
	def getHumidity(self):
		self.update()
		return self.hum
