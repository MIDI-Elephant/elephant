#!/usr/bin/python3
import OPi.GPIO as GPIO
import i2clcd as LCD
from time import sleep
import KeypadThread
import queue
import threading
import atexit
from config_elephant import *


char_queue=queue.Queue(10)
    
def setup_gpio():
    
    GPIO.setboard(GPIO.ZERO)        # Orange Pi Zero board
    GPIO.setmode(GPIO.BOARD)        # set up BOARD GPIO numbering
    for pin in all_board_pins:
        if pin == None:
            continue
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF) 
    
class GPIOReadcharThread(threading.Thread):
    
    first_repeat_wait = .1
    normal_repeat_wait = .1
    total_repeat_count = 4
        
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.output_queue=char_queue
       self.elephant=elephant
       atexit.register(self.cleanup)
     
    def get_output_queue(self):
        return self.output_queue
    
    def run(self):
        print("GPIOKeypadThread is running...")
        setup_gpio()
        sleep(1)
        while True:
            sleep(.08)
            try:
                for pin in all_board_pins:
                    # headless platform only has one switch
                    if pin == None:
                        continue
                    if GPIO.input(pin):
                       char = board_pin_to_char[pin]
                       self.output_queue.put(char)
                       if (pin != FORWARD_BOARD and pin != BACK_BOARD
                           and pin != STOP_BOARD):
                           while GPIO.input(pin):
                               pass
                            
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    sys.exit(0)
                else:
                    print(f"Exception in while loop: {e}")
            
            
    def cleanup(self):
        print("Cleaning up GPIO")
        GPIO.cleanup()
            
if __name__ == '__main__':
    
    gpio_keypad = GPIOReadcharThread(name="gpio")
    
    gpio_keypad.start()
    
    output_queue = gpio_keypad.get_output_queue()
    
    while True:
        char = output_queue.get()
        print(f"Got char '{char}'")
   