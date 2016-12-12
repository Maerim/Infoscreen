import Adafruit_DHT

class AM2302:
	
	def __init__(self, pin):
		self.temp = 0.0
		self.hum = 0.0
		self.pin = pin
		self._update()
	
	def _update(self):
		humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, self.pin)
		
		if humidity == None:
			humidity = 0.0
		if temperature == None:
			temperature = 0.0
		
		self.temp = temperature
		self.hum = humidity
	
	def get_data(self):
		self._update()
		return((self.temp, self.hum))