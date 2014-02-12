import wiringpi2, time

wiringpi2.wiringPiSetup() 

wiringpi2.pinMode(1,2)
wiringpi2.pwmWrite(1, 1000)