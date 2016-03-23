#!/usr/bin/python3

# ===============
# Jethro Hemmann
# Oktober 2013
# ===============


import RPi.GPIO as GPIO
from time import sleep
import math
import font
import wiringpi2
from Framebuffer import Framebuffer

#GPIO.setwarnings(False)

class LCD(object):

	DELAY_E = 0.000005 # 5 us

	def __init__(self, CS1, CS2, E, RS, D0, D1, D2, D3, D4, D5, D6, D7, PWM):
		self.CS1 = CS1
		self.CS2 = CS2
		self.E = E
		self.RS = RS
		self.D0 = D0
		self.D1 = D1
		self.D2 = D2
		self.D3 = D3
		self.D4 = D4
		self.D5 = D5
		self.D6 = D6
		self.D7 = D7
		self.PWM = PWM
		
		# initialize new framebuffer
		self.myFrameBuffer = Framebuffer()
		
		# setup wiringPi for backlight PWM
		wiringpi2.wiringPiSetup()
		wiringpi2.pinMode(self.PWM,2) # setup wiringPi pin for PWM		   
		
		GPIO.setmode(GPIO.BCM)
		
		GPIO.setup(self.CS1, GPIO.OUT, initial=0)
		GPIO.setup(self.CS2, GPIO.OUT, initial=0)
		GPIO.setup(self.E, GPIO.OUT, initial=0)
		GPIO.setup(self.RS, GPIO.OUT, initial=1)
		GPIO.setup(self.D0, GPIO.OUT, initial=0)
		GPIO.setup(self.D1, GPIO.OUT, initial=0)
		GPIO.setup(self.D2, GPIO.OUT, initial=0)
		GPIO.setup(self.D3, GPIO.OUT, initial=0)
		GPIO.setup(self.D4, GPIO.OUT, initial=0)
		GPIO.setup(self.D5, GPIO.OUT, initial=0)
		GPIO.setup(self.D6, GPIO.OUT, initial=0)
		GPIO.setup(self.D7, GPIO.OUT, initial=0)
		
		sleep(self.DELAY_E)
		self.turnOn()
		self.setStartLine(0)
		self.clearScreen()
		self.setPage(0) # start on top left
		self.setAddress(1)
	
	def turnOn(self):
		self.setByte(0x3F,0,1,1)
		
	def setByte(self, dataByte, RS, CS1=2, CS2=2):
		# if CSx=2, do not change chip! default!
		# RS=1: data, RS=0: instruction
		
		# CS=1 = active! (high active)
		if CS1 != 2 and CS2 != 2:
			GPIO.output(self.CS1, CS1)
			GPIO.output(self.CS2, CS2)
		
		GPIO.output(self.RS, RS)
		GPIO.output(self.D0, dataByte & 0x01)
		GPIO.output(self.D1, dataByte & 0x02)
		GPIO.output(self.D2, dataByte & 0x04)
		GPIO.output(self.D3, dataByte & 0x08)
		GPIO.output(self.D4, dataByte & 0x10)
		GPIO.output(self.D5, dataByte & 0x20)
		GPIO.output(self.D6, dataByte & 0x40)
		GPIO.output(self.D7, dataByte & 0x80)
		#print(dataByte)
		self.enable()
		
	def enable(self):
		
		#sleep(self.DELAY_E)
		GPIO.output(self.E, 1)
		sleep(self.DELAY_E)
		GPIO.output(self.E, 0)
		#sleep(self.DELAY_E)

	def drawPoint(self, x, y):
		page = math.ceil((65-y)/8)-1 # convert in LCD coordinate system and select corresponding page
		
		self.setPage(page)
		self.setAddress(x)

		currentByte = self.myFrameBuffer.getFramebufferByte(x,page)

		byte = currentByte | (1<<((64-y)%8)) # use shift operator to set byte
		#print(str(currentByte) + ' ' + str(byte))
		self.setByte(byte,1) # do not change chip
		self.myFrameBuffer.setFramebufferByte(x,page,byte)
	
	def setAddress(self, y): # set address in pixels!! (1-128)
		GPIO.output(self.RS, 0)
		
		if y-1 < 64:
			byte = (y-1) | 0x40
			self.setByte(byte,0,1,0) # write byte to chip 1
		else:
			byte = (y-65) | 0x40
			self.setByte(byte,0,0,1) # wirte byte to chip 2
		
	def setPage(self, page): # set page (0-7) on both chips
		byte = page | 0xB8
		# set byte on both chips
		self.setByte(byte,0,1,0)
		self.setByte(byte,0,0,1)   
	
	def clearScreen(self):
		#clear both chips
		for i in range(8):
			self.setPage(i)
			for j in range(64):
				self.setByte(0x00,1,1,1)
				
	def setStartLine(self, line): # line = 0-63, 0 = bottom
		byte = line | 0xC0
		self.setByte(byte,0,1,1)
	
	def printCharacter(self, char, CS1, CS2):
		asciiCode = ord(char)
		
		for i in range(8):
			self.setByte(font.chars[asciiCode][i],1,CS1,CS2)
		
	def printString(self, string, page):
		if len(string) < 16: # add white space at end if string shorter than one line --> clears rest of the line
			string = string + ' '*(16-len(string))
		CS1 = 1 # begin on chip 1
		CS2 = 0
		self.setPage(page)
		self.setAddress(1)
		
		for i, char in enumerate(string):
			self.printCharacter(char, CS1, CS2)
			if (i+1)%8==0: # change chip after 8 characters
				CS1 = ~CS1 & 0x01 # invert bit (see: http://stackoverflow.com/questions/7278779/bit-wise-operation-unary-invert)
				CS2 = ~CS2 & 0x01
				self.setAddress(65) # set first pixel
				
			#if (i+1)%16 == 0: # change line after 16 characters (page)
			#	page=page+1
			#	self.setPage(page)
			#	self.setAddress(1)

	def setBacklightPWM(self, value):
		wiringpi2.pwmWrite(self.PWM, value)