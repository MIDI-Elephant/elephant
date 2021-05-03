#!/usr/bin/python3
import OPi.GPIO as GPIO
import i2clcd as LCD
from time import sleep
import KeypadThread
import queue
import threading
import atexit
import logging
from config_elephant import *

bcm_channel_to_board_pin = {
    12  :   3,
    11  :   5,
    6   :   7,
    198 :   8,
    199 :   10,
    1   :   11,
    7   :   12,
    0   :   13,
    3   :   15,
    19  :   16,
    18  :   18,
    15  :   19,
    16  :   21,
    2   :   22,
    14  :   23,
    13  :   24,
    10  :   26
}   

class GPIOInterruptReadcharThread(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    first_repeat_wait = .1
    normal_repeat_wait = .1
    total_repeat_count = 4
    bouncetime=.02
        
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.lock = threading.Lock()
       self.bouncetime=.01
       self.output_queue=queue.Queue(50)
       self.elephant=elephant
       atexit.register(self.cleanup)
       
    def setup_gpio(self):
        self.logger.debug("Setting up GPIO")
        GPIO.setboard(GPIO.ZERO)        # Orange Pi Zero board
        GPIO.setmode(GPIO.BOARD)        # set up BOARD GPIO numbering
       
        for pin in all_board_pins:
            if pin == None:
                continue
            self.logger.debug(f"Setting up for pin {pin}")
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(pin, GPIO.RISING, callback=self) 
    
    def get_output_queue(self):
        return self.output_queue
    
    def __call__(self, *args):
        self.logger.debug(f"Internal callback called with channel={args[0]}")
        if not self.lock.acquire(blocking=False):
            return
        
        board_pin = bcm_channel_to_board_pin[args[0]]
        self.logger.debug(f"Checking board pin {board_pin}")
        if GPIO.input(board_pin):
            self.logger.debug(f"board pin was HIGH")
        
        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()
        
    def read(self, *args):
        
        self.logger.debug(f"Read called with channel={args[0]}")
        if args[0] in bcm_channel_to_board_pin.keys():
            board_pin = bcm_channel_to_board_pin[args[0]]
            char = board_pin_to_char[board_pin]
            sleep(self.bouncetime)
            self.logger.debug(f"Checking board pin {board_pin}")
            if GPIO.input(board_pin):
                self.logger.debug(f"board pin was HIGH")
           # sleep(self.normal_repeat_wait)
            self.logger.debug(f"Putting char '{char}' into output queue")
            self.output_queue.put(char)
        else:
            self.logger.debug(f"Channel {args[0]} not found")
        
        self.lock.release()
        
    
    def run(self):
        print("GPIOKeypadThread is running...")
        self.setup_gpio()
        
        while True:
            sleep(1)
            
    def cleanup(self):
        print("Cleaning up GPIO")
        GPIO.cleanup()
            
if __name__ == '__main__':
    
    gpio_keypad = GPIOInterruptReadcharThread(name="gpio")
    
    gpio_keypad.start()
    
    output_queue = gpio_keypad.get_output_queue()
    
    while True:
        char = output_queue.get()
        print(f"Got char '{char}'")
   