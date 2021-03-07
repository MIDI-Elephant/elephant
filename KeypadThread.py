import sys 
import time
import threading
import logging
import queue
from queue import Empty
from ElephantCommon import event_map as event_map
from ElephantCommon import *

use_lcd = False

try:
    import i2clcd as LCD
    use_lcd = True
except:
    pass

try:
    import OPi.GPIO as GPIO
    from GPIOReadcharThread import GPIOReadcharThread as readchar
    use_gpio = True
    first_repeat_wait = .1
    normal_repeat_wait = .1
    print("Using GPIOReadCharThread")
except:
    use_gpio = False
    from TerminalReadcharThread import TerminalReadcharThread as readchar
    first_repeat_wait = .5
    normal_repeat_wait = .1
    print("Using TerminalReadcharThread")

class KeypadThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.output_queue=queue.Queue(5)
        self.readchar_thread=None
        self.input_queue=None
       
    def get_output_queue(self):
        return self.output_queue
    
    def is_held_char(self, charToCheck):
     repeat_count = 0
     repeat_wait = first_repeat_wait
     while True:
        try: 
            buttonChar = self.input_queue.get(timeout=repeat_wait)
        except Empty as empty:
            return False

        if (buttonChar != charToCheck):
            return False

        repeat_count  += 1
        repeat_wait = normal_repeat_wait

        if repeat_count == 2:
            return True

    def is_held_char_timeout(self, charToCheck):
        while True:
            try: 
                buttonChar = self.input_queue.get(timeout=0.1)
            except Exception as exception:
                return True

        return False
       
    def run(self):
        
        self.readchar_thread=readchar(self)
        self.readchar_thread.start()
        
        print("EventThread is running...")
        seek_event = False
        checking_for_seek = False
        last_char_pressed_time = time.perf_counter()
        lastChar = ' '
        seek_check_iteration = 0
        self.input_queue = self.readchar_thread.get_output_queue()
        
        while True:
            buttonChar = self.input_queue.get()
            
            if (not buttonChar in event_map.keys()):
                print(f"Invalid character {buttonChar}")
                continue
            
            if (buttonChar != 'b' and buttonChar != 'f'):
                try:
                    self.output_queue.put(buttonChar)
                except Exception as exception:
                    print(exception)
                
            else:
                if self.is_held_char(charToCheck = buttonChar):
                    charToPut = back_forward_to_seek_map[buttonChar]
                    self.output_queue.put(charToPut)

                    while not self.is_held_char_timeout(charToCheck = buttonChar):
                        pass
                    
                    charToPut = back_forward_to_seek_release_map[buttonChar]
                else:
                    charToPut = buttonChar.upper()
                    
                self.output_queue.put(charToPut)

        return
  
       
