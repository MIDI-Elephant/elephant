import threading
import logging
import time
from time import sleep as sleep
from ElephantCommon import *

try:
    import OPi.GPIO as GPIO
    import GPIOThread
    use_gpio = True
except:
    pass

ON=1
OFF=2
BLINKING=3

class LEDManager(threading.Thread):
    def __init__(self, name, led_pin):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.led_pin=led_pin
       self.state = OFF
       
       GPIO.setboard(GPIO.ZERO)  
       GPIO.setmode(GPIO.BOARD)
       GPIO.setup(self.led_pin, GPIO.OUT)
       GPIO.output(self.led_pin, False)   
       
    def _led_on(self):
        GPIO.output(self.led_pin, True)
        
    def _led_off(self):
        GPIO.output(self.led_pin, False)
       
    def led_on(self):
        self.state=ON
    
    def led_off(self):
        self.state=OFF
        
    def led_blink_on(self):
        self.state=BLINKING
     
    def led_blink_off(self):
       self.state=OFF
        
    def run(self):
        while True:
            if self.state == BLINKING:
                self._led_on()
                sleep(.75)
                self._led_off()
                sleep(.75)
            elif self.state == ON:
                self._led_on()
                sleep(.2)
            else:
                self._led_off()
                sleep(.2)

        
    
