import sys 
import time
import threading
import logging
import queue
import importlib
from queue import Empty
import Elephant
from ElephantCommon import event_map as event_map
from ElephantCommon import *


class KeypadThread(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    def __init__(self, name, command_data_plugin_name=None, elephant=None):
        threading.Thread.__init__(self)
        self.name = name
        self.output_queue=queue.Queue(50)
        self.readchar_thread=None
        self.input_queue=None
        self.command_data_plugin_name=command_data_plugin_name
        self.elephant=elephant
       
    def get_output_queue(self):
        return self.output_queue
    
    def is_held_char(self, charToCheck):
     repeat_count = 0
     repeat_wait = self.readchar_thread.first_repeat_wait
     while True:
        try: 
            buttonChar = self.input_queue.get(timeout=repeat_wait)
        except Empty as empty:
            return False

        if (buttonChar != charToCheck):
            return False

        repeat_count  += 1
        repeat_wait = self.readchar_thread.normal_repeat_wait

        if repeat_count == self.readchar_thread.total_repeat_count:
            #print(f"#### IS_REPEAT_CHAR=True, char='{charToCheck}'")
            return True

    def is_held_char_timeout(self, charToCheck):
        while True:
            try: 
                buttonChar = self.input_queue.get(timeout=0.1)
            except Exception as exception:
                return True

        return False
       
    def run(self):
        
        module=importlib.import_module(self.command_data_plugin_name)
        readchar=getattr(module, self.command_data_plugin_name)
        
        self.readchar_thread=readchar(self, elephant=self.elephant)
        self.readchar_thread.start()
        
        self.logger.debug("KeypadThread is running...")
        seek_event = False
        checking_for_seek = False
        last_char_pressed_time = time.perf_counter()
        lastChar = ' '
        seek_check_iteration = 0
        self.input_queue = self.readchar_thread.get_output_queue()
        
        while True:
            buttonChar = self.input_queue.get()
            self.logger.debug(f"Got char '{buttonChar}' from queue")
            if (not buttonChar in event_map.keys()):
                self.logger.debug(f"Invalid character {buttonChar}")
                continue
            
            # If it's not a character that can be repeated
            if (buttonChar not in characters_that_can_repeat):
                try:
                    self.output_queue.put(buttonChar)
                except Exception as exception:
                    self.logger.exception(exception)
                 
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
  
if __name__ == '__main__':   
    
    keypad=KeypadThread("test", 'GPIOReadcharThread', None)
    keypad.start()
    
    while True:
        time.sleep(1)
        
