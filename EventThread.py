from transitions import Machine
from transitions import State
import threading
import logging
import queue
from queue import Empty
import time
import KeypadThread
from ElephantCommon import *


#
# This class generates events by using input from a standard keyboard
# and translating the input to the appropriate set of internal events. It's
# main purpose is to allow for development on a system with full IDE/debugger
# capabilities prior to deployment on a SBC like a Raspberry Pi etc.
#
# Once events are recognized, they are put onto a FIFO queue, the event_queue, 
# and that thread, in turn, calls the trigger methods on the class that is bound
# as a state machine.   

#
class EventThread(threading.Thread):
    def __init__(self, name, 
                 state_machine=None, event_queue=None,
                 command_data_plugin_name='TerminalReadcharThread'):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.event_queue = event_queue
       self.state_machine = state_machine
       self.name = name
       self.command_data_plugin_name=command_data_plugin_name


    def is_held_char(self, charToCheck):
         repeat_count = 0
         first_repeat_wait = .55
         normal_repeat_wait = .1
         repeat_wait = first_repeat_wait
         while True:
            try: 
                buttonChar = self.char_queue.get(timeout=repeat_wait)
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
                buttonChar = self.characterQueue.get(timeout=0.1)
            except Exception as exception:
                return True

        return False
    

    def run(self):
        print(f"EventThread for {self.name} started...")
        
       
        keypadThread = KeypadThread.KeypadThread(self.command_data_plugin_name, 
                                                 self.command_data_plugin_name,
                                                 elephant=self.state_machine)
        
        keypadThread.start()
        
        print("EventThread is running...")
        seek_event = False
        checking_for_seek = False
        last_char_pressed_time = time.perf_counter()
        lastChar = ' '
        seek_check_iteration = 0
        input_queue = keypadThread.get_output_queue()
        while True:
            buttonChar = input_queue.get()
            try:
                trigger_method = event_map[buttonChar]
                self.event_queue.put(trigger_method)
            except Exception as exception:
                print(exception)

        return


