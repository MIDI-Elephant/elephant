import threading
import logging
import time
from time import sleep as sleep
from config_elephant import *

try:
    import OPi.GPIO as GPIO
    import GPIOThread
    use_gpio = True
except:
    pass

c_green='green'
c_red='red'
c_yellow='yellow'
c_orange='orange'


color_dict = {
                c_green : (.0083, 0), 
                c_red : (0, .0083), 
                c_yellow : (.00680, .00200),
                c_orange : (.00275, .00623) 
                }
led_dict = {
            'midi' : (MIDI_GREEN, MIDI_RED),
            'elephant' : (STATUS_GREEN, STATUS_RED)
            }

IDX_GREEN_LED_INTERVAL=0
IDX_RED_LED_INTERVAL=1

IDX_GREEN_LED_PIN=0
IDX_RED_LED_PIN=1

BLINK_SPECIFIER='b'
FLASH_SPECIFIER='f'


ON=1
OFF=2
IDLE=3
SLEEPING=3
BLINKING=4
FLASHING=5




class ColorLEDThread(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    def __init__(self, ledmanager):
        threading.Thread.__init__(self)
        self.name=ledmanager.name
        self.ledmanager=ledmanager
        self.led_name=ledmanager.led_name
        self.green_pin=ledmanager.green_pin
        self.red_pin=ledmanager.red_pin
        self.color=None
        self.isRunning=True
        self.event=threading.Event()
        self.colorthreadsync=threading.Event()
        self.colorthreadsync.clear()
        
        GPIO.setboard(GPIO.ZERO)  
        GPIO.setmode(GPIO.BOARD)
        
        led_pins_tuple=led_dict[self.led_name]
       
        for pin in list(led_pins_tuple):
            if pin is None:
                continue
            print(f"Setting up name={self.name}, pin {pin} as output")
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)
           
        self.green_pin=led_pins_tuple[IDX_GREEN_LED_PIN]
        self.red_pin=led_pins_tuple[IDX_RED_LED_PIN]
        
        
    def stop(self):
        self.isRunning=False
        self.event.set()
        
    def reset(self):
       self.led_off()
        
    
    def led_on(self, color):
        if color == c_green:
            GPIO.output(self.green_pin, True)
        elif color == c_red:
            GPIO.output(self.red_pin, True)
        else:
            self.set_color(color)
            self.event.set()
        
    def led_off(self):
        if self.event.isSet():
            self.event.clear()
            self.colorthreadsync.wait()
        
        if self.color == c_green:
            GPIO.output(self.green_pin, False)
        elif self.color == c_red:
            GPIO.output(self.red_pin, False)
        else:
           # self.logger.debug(f"Entering _led_off()")
            led_pins_tuple=led_dict[self.led_name]
            for pin in list(led_pins_tuple):
                GPIO.output(pin, False)
         
    def set_color(self, color):
        self.color=color
        if color != c_green and color != c_red:
            color_params = color_dict[color]
            self.green_interval = color_params[IDX_GREEN_LED_INTERVAL]
            self.red_interval = color_params[IDX_RED_LED_INTERVAL] 
 
    def run(self):
        #self.logger.debug(f"ColorLEDThread running for {self.name}")
        while self.isRunning:
            self.colorthreadsync.clear()
            self.event.wait()
            if not self.isRunning:
                break
        
            #self.logger.debug(f"Running color LED loop")
            while self.event.isSet() and self.isRunning:
                GPIO.output(self.green_pin, True)
                sleep(self.green_interval)
                GPIO.output(self.green_pin, False)
                GPIO.output(self.red_pin, True)
                sleep(self.red_interval)
                GPIO.output(self.red_pin, False)
            
            self.colorthreadsync.set()
                
        #self.logger.debug(f"ColorLEDThread for {self.led_name} stopped.")    
            
class MultiColorLEDManager(threading.Thread):
    logger=logging.getLogger(__name__)
    
    def __init__(self, led_name, blink_delay=DEFAULT_BLINK_DELAY):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.name=led_name
        self.led_name=led_name
        self.state=OFF
        self.blink_delay=blink_delay
        self.green_pin=None
        self.red_pin=None
        self.isBlinking=False
        self.color=None
        self.color_name=None
        self.isRunning = True
        self.blinkevent=threading.Event()
        self.blinkevent.clear()
        self.blinksync=threading.Event()
        self.blinksync.clear()
        self.colorthread=None
        
    def _set_color(self, color):
        color_elements=color.split(":")
        #self.logger.debug(f"color_elements={color_elements}")
        color_name=color_elements[0]
        self.color=color
        self.color_name=color_name
        if len(color_elements) == 2:
            #self.logger.debug(f"Setting up for blinking, specifier={color_elements[1]}")
            if color_elements[1] == BLINK_SPECIFIER:
                self.state=BLINKING
                self.blink_delay=DEFAULT_BLINK_DELAY
            elif color_elements[1] == FLASH_SPECIFIER:
                self.state=BLINKING
                self.blink_delay=(DEFAULT_BLINK_DELAY/4)
        
        color_params = color_dict[color_name]
        self.green_interval = color_params[IDX_GREEN_LED_INTERVAL]
        self.red_interval = color_params[IDX_RED_LED_INTERVAL]
        
    def reset(self):
        self.state=None
        if self.blinkevent.isSet():
            self.blinkevent.clear()
            #self.logger.debug(f"Waiting for blink thread to exit...")
            self.blinksync.wait()
            #self.logger.debug("Synchronized with blink thread...")
        self.colorthread.reset()
        
    def _led_on(self):
        self.colorthread.led_on(self.color_name)
        
    def _led_off(self):
        self.colorthread.led_off()
    
    def indicator_on(self, indicator_spec):
        #self.logger.debug(f"LED Manager {self.led_name} setting indicator {indicator_spec}")
        self.reset()
        self._set_color(indicator_spec)
        if self.state == BLINKING:
            self.led_blink_on(indicator_spec)
        else:
            #self.logger.debug("Turning LED ON!")
            self._led_on()
       
    def led_on(self, color):
        self._set_color(color)
        self._led_on()

    def led_off(self):
       self._led_off()
        
    def led_blink_on(self, color):
        self._set_color(color)
        self.blinkevent.set()
     
    def led_blink_off(self):
        self.blinkevent.clear()
       
    def led_flash_on(self, color):
        self.blink_delay=DEFAULT_BLINK_DELAY/4
        self.led_blink_on(color)
        
    def led_flash_off(self):
        self.led_blink_off()
       
    def stop(self):
        #self.logger.debug(f"Shutting down LED {self.name}")
        self.colorthread.stop()
        self.isRunning = False
        self.blinkevent.set()
        
    def run(self):
        self.colorthread=ColorLEDThread(self)
        self.colorthread.start()
        self.logger.debug(f"LED Manager Thread {self.name} started!")
        while self.isRunning:
            # This looks pretty unorthodox but it's here to allow
            # for the lowest possible latency when switching from
            # blinking to on
            #self.logger.debug("waiting for blink event")
            self.blinksync.clear()
            self.blinkevent.wait()
            if not self.isRunning:
                break
            #self.logger.debug("entering blink loop")
            while self.blinkevent.isSet():
                for blinking_state in [OFF, SLEEPING, ON, SLEEPING]:
                    if not self.blinkevent.isSet():
                        break
                    if blinking_state == ON:
                        self._led_on()
                    elif blinking_state == SLEEPING:
                        sleep_start_time=time.perf_counter()
                        sleep_end_time=sleep_start_time + self.blink_delay
                        while time.perf_counter() < sleep_end_time:
                            if not self.blinkevent.isSet():
                                break
                            sleep(.005)
                    elif blinking_state == OFF:
                        self._led_off()
            #self.logger.debug("Exiting blink loop")
            self.blinksync.set()
                


        
    
