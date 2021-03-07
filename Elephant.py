
import sys 
import time
from time import sleep as sleep
import transitions
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
import asyncio
from transitions import State
import threading
import logging
import queue
from queue import Empty
import Elephant
import EventThread
import KeypadThread
from ElephantCommon import *
from ElephantCommon import event_map as event_map
import LEDManager

use_lcd = False
use_gpio = False

try:
    import i2clcd as LCD
    use_lcd = True
    lcd = LCD.i2clcd(i2c_bus=0, i2c_addr=0x27, lcd_width=20)
    lcd.init()
except:
    pass

try:
    import OPi.GPIO as GPIO
    use_gpio = True
    import GPIOReadcharThread
except:
    pass


def lprint(text):
    lcd.clear()
    lcd.print_line(text, 0)

def display(text):
    if use_lcd:
        lprint(text)
        print(text)
    else:
        print(text)

    
states = [
          State(
              name=S_STOPPED, 
              on_enter=['e_stopped'],
              on_exit=['x_stopped']
              ),
          State(
              name=S_PLAYING, 
              on_enter=['e_playing'],
              on_exit=['x_playing']
              ),
          State(
              name=S_PLAYING_PAUSED,
              on_enter=['e_playing_paused'],
              on_exit=['x_playing_paused']
              ), 
          State(
              name=S_RECORDING,
              on_enter=['e_recording'],
              on_exit=['x_recording']
              ), 
          State(
              name=S_RECORDING_PAUSED,
              on_enter=['e_recording_paused'], 
              on_exit=['x_recording_paused']
              ),
          State(
              name=S_SAVING_RECORDING, 
              on_enter=['e_saving_recording'],
              on_exit=['x_saving_recording']
              ), 
          State(
              name=S_SKIP_BACK_WHILE_STOPPED,
              on_enter=['e_skip_back_while_stopped'],
              on_exit=['x_skip_back_while_stopped']
              ), 
          State(
              name=S_SKIP_FORWARD_WHILE_STOPPED,
              on_enter=['e_skip_forward_while_stopped'],
              on_exit=['x_skip_forward_while_stopped']
              ),
          State(
              name=S_SKIP_BACK_WHILE_PLAYING,
              on_enter=['e_skip_back_while_playing'],
              on_exit=['x_skip_back_while_playing']
              ), 
          State(
              name=S_SKIP_FORWARD_WHILE_PLAYING,
              on_enter=['e_skip_forward_while_playing'],
              on_exit=['x_skip_forward_while_playing']
              ),
          
          State(
              name=S_SKIP_BACK_WHILE_PLAYING_PAUSED,
              on_enter=['e_skip_back_while_playing_paused'],
              on_exit=['x_skip_back_while_playing_paused']
              ), 
          State(
              name=S_SKIP_FORWARD_WHILE_PLAYING_PAUSED,
              on_enter=['e_skip_forward_while_playing_paused'],
              on_exit=['x_skip_forward_while_playing_paused']
              ),
          State(
              name=S_SEEKING_BACK,
              on_enter=['e_seeking_back'],
              on_exit=['x_seeking_back']
              ), 
          State(
              name=S_SEEKING_FORWARD,
              on_enter=['e_seeking_forward'],
              on_exit=['x_seeking_forward']
              ),
          State(
              name=S_WAITING_FOR_MIDI,
              on_enter=['e_waiting_for_midi']
              ),
          State(
              name=S_AUTO_RECORDING,
              on_enter=['e_auto_recording']
              ),
          State(
              name=S_AUTO_SAVING,
              on_enter=['e_auto_saving']
              ),
          ]

transitions = [
        # States from Stopped
        [ E_SKIP_BACK, S_STOPPED, S_SKIP_BACK_WHILE_STOPPED ],
        [ E_PREVIOUS_TRACK, S_SKIP_BACK_WHILE_STOPPED, S_STOPPED ],
        [ E_SKIP_FORWARD, S_STOPPED, S_SKIP_FORWARD_WHILE_STOPPED ],
        [ E_NEXT_TRACK, S_SKIP_FORWARD_WHILE_STOPPED, S_STOPPED ],
        
        # Playing
        [ E_PLAY_PAUSE_BUTTON, S_STOPPED, S_PLAYING ],
        [ E_PLAY_PAUSE_BUTTON, S_PLAYING, S_PLAYING_PAUSED ],
        [ E_PLAY_PAUSE_BUTTON, S_PLAYING_PAUSED, S_PLAYING ],
        [ E_END_OF_TRACK, S_PLAYING, S_STOPPED ],
        [ E_STOP_BUTTON, S_PLAYING, S_STOPPED ],
        [ E_STOP_BUTTON, S_PLAYING_PAUSED, S_STOPPED ],
        
        [ E_SKIP_BACK, S_PLAYING, S_SKIP_BACK_WHILE_PLAYING ],
        [ E_PREVIOUS_TRACK, S_SKIP_BACK_WHILE_PLAYING, S_PLAYING ],
        [ E_SKIP_FORWARD, S_PLAYING, S_SKIP_FORWARD_WHILE_PLAYING ],
        [ E_NEXT_TRACK, S_SKIP_FORWARD_WHILE_PLAYING, S_PLAYING ],
        
        [ E_SKIP_BACK, S_PLAYING_PAUSED, S_SKIP_BACK_WHILE_PLAYING_PAUSED ],
        [ E_PREVIOUS_TRACK, S_SKIP_BACK_WHILE_PLAYING_PAUSED, S_PLAYING_PAUSED ],
        [ E_SKIP_FORWARD, S_PLAYING_PAUSED, S_SKIP_FORWARD_WHILE_PLAYING_PAUSED ],
        [ E_NEXT_TRACK, S_SKIP_FORWARD_WHILE_PLAYING_PAUSED, S_PLAYING_PAUSED ],
        
        [ E_SEEK_BACK, S_PLAYING, S_SEEKING_BACK ],
        [ E_SEEK_BACK_RELEASED, S_SEEKING_BACK, S_PLAYING],
        [ E_SEEK_FORWARD, S_PLAYING, S_SEEKING_FORWARD ],
        [ E_SEEK_FORWARD_RELEASED, S_SEEKING_FORWARD, S_PLAYING],
        
        # Recording
        [ E_RECORD_BUTTON, S_STOPPED, S_RECORDING ],
        [ E_RECORD_BUTTON, S_RECORDING, S_SAVING_RECORDING ],
        [ E_RECORD_BUTTON, S_RECORDING_PAUSED, S_SAVING_RECORDING ],
        [ E_STOP_BUTTON, S_RECORDING, S_SAVING_RECORDING ],
        [ E_PLAY_PAUSE_BUTTON, S_RECORDING, S_RECORDING_PAUSED ],
        [ E_PLAY_PAUSE_BUTTON, S_RECORDING_PAUSED, S_RECORDING ],
        [ E_STOP_BUTTON, S_RECORDING_PAUSED, S_SAVING_RECORDING ],
        [ E_RECORDING_SAVED, S_SAVING_RECORDING, S_STOPPED ],
        
        # Auto-recording
        [ E_AUTO_RECORD_BUTTON, S_STOPPED, S_WAITING_FOR_MIDI ],
        [ E_MIDI_DETECTED, S_WAITING_FOR_MIDI, S_AUTO_RECORDING ],
        [ E_MIDI_PAUSED, S_AUTO_RECORDING, S_AUTO_SAVING ],
        [ E_RECORDING_SAVED, S_AUTO_SAVING, S_WAITING_FOR_MIDI ],
        [ E_STOP_BUTTON, S_AUTO_RECORDING, S_SAVING_RECORDING ],
        [ E_PLAY_PAUSE_BUTTON, S_RECORDING_PAUSED, S_RECORDING ],
        [ E_STOP_BUTTON, S_WAITING_FOR_MIDI, S_STOPPED ],
        ]


class Elephant(threading.Thread):
    
    def __init__(self, name, state_machine=None, event_queue=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.event_queue = event_queue
       self.state_machine = self
       self.name = name
       self.led_manager = None

    def raise_event(self, event_name):
        try:
            self.event_queue.put(event_name)
        except Exception as exception:
            print(exception)

    def e_default(self, event_data): 
        print(event_data.transition)
        display(self.state)
        
    def e_waiting_for_midi(self, event_data): 
        print(event_data.transition)
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_blink_on()
        sleep(5)
        if (self.state != S_STOPPED):
            self.raise_event(E_MIDI_DETECTED)
        
    def e_auto_recording(self, event_data): 
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_on()
        sleep(5)
        if (self.state != S_STOPPED):
            self.raise_event(E_MIDI_PAUSED)
        
    def e_auto_saving(self, event_data): 
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_off()
        sleep(1)
        self.raise_event(E_RECORDING_SAVED)
     
    def e_playing(self, event_data): 
        print(event_data.transition)
        display(self.state)

    def x_playing(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_playing_paused(self, event_data): 
        display(self.state)

    def x_playing_paused(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_recording(self, event_data): 
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_on()

    def x_recording(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def x_recording(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_recording_paused(self, event_data):
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_blink_on()

    def x_recording_paused(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_saving_recording(self, event_data) : 
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_off()
        sleep(1)
        self.raise_event(E_RECORDING_SAVED)
       

    def x_saving_recording(self, event_data) :
        pass

    def e_stopped(self, event_data) :
        display(self.state)
        if self.led_manager != None:
            self.led_manager.led_off()

    def x_stopped(self, event_data) :
        pass
    
    def e_skip_back_while_stopped(self, event_data): 
        print(event_data.transition)
        display(self.state)
        sleep(1)
        self.raise_event(E_PREVIOUS_TRACK)

    def x_skip_back_while_stopped(self, event_data): 
        pass
    
    def e_skip_back_while_playing(self, event_data): 
        print(event_data.transition)
        display(self.state)
        sleep(1)
        self.raise_event(E_PREVIOUS_TRACK)

    def x_skip_back_while_playing(self, event_data): 
        pass

    def e_skip_back_while_playing_paused(self, event_data): 
        print(event_data.transition)
        display(self.state)
        sleep(1)
        self.raise_event(E_PREVIOUS_TRACK)

    def x_skip_back_while_playing_paused(self, event_data): 
        pass
    
    def e_skip_forward_while_stopped(self, event_data): 
        print(event_data.transition)
        display(self.state)
        sleep(1)
        self.raise_event(E_NEXT_TRACK)

    def x_skip_forward_while_stopped(self, event_data): 
        pass
    
    def e_skip_forward_while_playing(self, event_data): 
        print(event_data.transition)
        display(self.state)
        sleep(1)
        self.raise_event(E_NEXT_TRACK)

    def x_skip_forward_while_playing(self, event_data): 
       pass
    
    def e_skip_forward_while_playing_paused(self, event_data): 
        print(event_data.transition)
        display(self.state)
        sleep(1)
        self.raise_event(E_NEXT_TRACK)

    def x_skip_forward_while_playing_paused(self, event_data): 
       pass
    
    def e_seeking_forward(self, event_data): 
        print(event_data.transition)
        display(self.state)

    def x_seeking_forward(self, event_data): 
        pass
    
    def e_seeking_back(self, event_data): 
        print(event_data.transition)
        display(self.state)

    def x_seeking_back(self, event_data): 
        pass
    
    def setup_state_machine(self):
        
        if use_gpio:
            led_manager = LEDManager.LEDManager("ledmanager", 
                                     GPIOReadcharThread.RECORD_STATUS_LED)
            led_manager.start()
            self.led_manager = led_manager
        
        self.machine = Machine(self, states=states, transitions=transitions, 
                               initial = 'Stopped', send_event=True)
        
        self.event_queue = queue.Queue(10)
        characterQueue = queue.Queue(10)
    
        event_thread = EventThread.EventThread(name='events',
                                   char_queue=characterQueue,
                                   state_machine=self,
                                   event_queue=self.event_queue)
        #readchar_thread.start()
        event_thread.start()
    
    
    def run(self):
        self.setup_state_machine()
        display("Elephant listening!")
        while True:
            if not self.event_queue.empty():
                trigger_method = self.event_queue.get()
                logging.debug('Getting ' + str(trigger_method)
                              + ' : ' + str(self.event_queue.qsize()) + ' items in queue')
                try:
                    print(f"Executing trigger method {trigger_method}")
                    getattr(self.state_machine, trigger_method)()
                except Exception as exception:
                    print(exception)
        return

if __name__ == '__main__':
    try:
        elephant_thread = Elephant(name='Elephant')
        elephant_thread.start()
        
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
