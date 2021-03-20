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
        self.output_queue=queue.Queue(10)
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
            
            # If it's not a character that can be repeated
            if (buttonChar not in characters_that_can_repeat):
                try:
                    self.output_queue.put(buttonChar)
                except Exception as exception:
                    print(exception)
                 
            else:
                # If it's a held character, map it to the appropriate character
                if self.is_held_char(charToCheck = buttonChar):
                    charToPut = held_character_translation_map[buttonChar]
                    self.output_queue.put(charToPut)

                    while not self.is_held_char_timeout(charToCheck = buttonChar):
                        pass
                    
                    charToPut = held_character_release_map[buttonChar]
                else:
                    charToPut = non_held_character_translation_map[buttonChar]
                 
                if (charToPut != ' '):
                    self.output_queue.put(charToPut)

        return
  
       
