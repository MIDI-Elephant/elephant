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
       
       self.isRunning = True
       
       GPIO.setboard(GPIO.ZERO)  
       GPIO.setmode(GPIO.BOARD)
       
       print(f"Setting up self={self}, name={self.name}, pin {self.led_pin} as output")
       GPIO.setup(self.led_pin, GPIO.OUT)
       GPIO.output(self.led_pin, False)   
       
       #GPIO.output(self.led_pin, True)
       #time.sleep(2)
       #GPIO.output(self.led_pin, True)
       
       
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
       
    def led_stop(self):
        print(f"Shutting down LED {self.name}")
        self.isRunning = False
        
    def run(self):
        
        print(f"LED Manager Thread {self.name} started!")
        
        GPIO.output(self.led_pin, True)
        time.sleep(2)
        GPIO.output(self.led_pin, True)
        
        while self.isRunning:
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
                
            state = ""
            try:
                if self.state == ON:
                    state = "ON"
                    self._led_on()
                    sleep(.2)
                else:
                    state = "OFF"
                    self._led_off()
                    sleep(.2)
            except Exception as e:
                print(f"Exception, state={state}, pin={self.led_pin}, {e}")
                break

        
    
