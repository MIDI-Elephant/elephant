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
SLEEPING=3
BLINKING=4

class LEDManager(threading.Thread):
    def __init__(self, name, led_pin, blink_delay=.75):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.led_pin=led_pin
       self.state = OFF
       self.blink_delay = blink_delay
       
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
            # This looks pretty unorthodox but it's here to allow
            # for the lowest possible latency when switching from
            # blinking to on
            while self.state == BLINKING:
                for blinking_state in [OFF, SLEEPING, ON, SLEEPING]:
                    if self.state == BLINKING:
                        if blinking_state == ON:
                            self._led_on()
                        elif blinking_state == SLEEPING:
                            sleep(self.blink_delay)
                        elif blinking_state == OFF:
                            self._led_off()
                    else:
                        break
                
            if self.state == ON:
                self._led_on()
                sleep(.2)
            else:
                self._led_off()
                sleep(.2)

        
    
