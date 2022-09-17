#!/usr/local/bin/python3
#######################################
#
#  Elephant top-level transport
#
#######################################
import asyncio
from datetime import datetime
import pdb
from queue import Empty
import queue
import sys 
import threading
import logging
from time import sleep as sleep
import time

from mido import MidiFile
import mido
from mido.ports import MultiPort

from transitions import Machine
from transitions import State
import transitions
from transitions.extensions.asyncio import AsyncMachine
#
import DisplayService
from ElephantCommon import *
from ElephantCommon import event_map as event_map
import EventThread
import KeypadThread
#import LEDManager
import MultiColorLEDManager
import MIDIEventService
import MidiFileManager
import PlaybackService
import RecordingService
import MIDIClockGenerator

from multiprocessing import Value
import atexit

import config_elephant as cfg
import yappi

import netifaces as ni

try:
    import i2clcd as LCD
    lcd = LCD.i2clcd(i2c_bus=0, i2c_addr=0x27, lcd_width=20)
    lcd.init()
    lcd.set_backlight(True)
except:
    pass

try:
    import OPi.GPIO as GPIO
    import GPIOReadcharThread
except:
    pass

try:
    import kmod
except:
    pass

def module_is_loaded(module):
    if cfg.use_kmod:
        k = kmod.Kmod()
        for tuple in k.list():
            if tuple[0] == module:
                return True
        return False
    else:
        return False
   
    
def load_kernel_module(module):
    if cfg.use_kmod:
        k = kmod.Kmod()
        k.modprobe(module)
    
def remove_kernel_module(module):
    if cfg.use_kmod:
        k = kmod.Kmod()
        if (module_is_loaded(module)):
            k.rmmod(module)
    
states = [
          State(
              name=S_READY, 
              on_enter=['e_ready'],
              on_exit=['x_ready']
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
              on_enter=['e_skip_back_while_ready'],
              on_exit=['x_skip_back_while_ready']
              ), 
          State(
              name=S_SKIP_FORWARD_WHILE_STOPPED,
              on_enter=['e_skip_forward_while_ready'],
              on_exit=['x_skip_forward_while_ready']
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
              on_enter=['e_waiting_for_midi'],
              on_exit=['x_waiting_for_midi']
              ),
          State(
              name=S_AUTO_RECORDING,
              on_enter=['e_auto_recording'],
              on_exit=['x_auto_recording'],
              ),
          State(
              name=S_AUTO_SAVING,
              on_enter=['e_auto_saving'],
              on_exit=['x_auto_saving'],
              ),
          State(
              name=S_CONTINUOUS_PLAYBACK_ENABLE,
              on_enter=['e_continuous_playback_enable']
              ),
          State(
              name=S_CONTINUOUS_PLAYBACK_DISABLE,
              on_enter=['e_continuous_playback_disable']
              ),
          State(
              name=S_TRACKING_SILENCE_ENABLE,
              on_enter=['e_tracking_silence_enable']
              ),
          State(
              name=S_TRACKING_SILENCE_DISABLE,
              on_enter=['e_tracking_silence_disable']
              ),
          State(
              name=S_MASS_STORAGE_ENABLED,
              on_enter=['e_mass_storage_enable']),
          State(
              name=S_MASS_STORAGE_DISABLING,
              on_enter=['e_mass_storage_disable'])
          ]

transitions = [
        # States from Stopped
        [ E_SKIP_BACK, S_READY, S_SKIP_BACK_WHILE_STOPPED ],
        [ E_PREVIOUS_FILE, S_SKIP_BACK_WHILE_STOPPED, S_READY ],
        [ E_NO_FILE, S_SKIP_BACK_WHILE_STOPPED, S_READY ],
        [ E_SKIP_FORWARD, S_READY, S_SKIP_FORWARD_WHILE_STOPPED ],
        [ E_NEXT_FILE, S_SKIP_FORWARD_WHILE_STOPPED, S_READY ],
        [ E_NO_FILE, S_SKIP_FORWARD_WHILE_STOPPED, S_READY ],
        #[ E_SWITCH_MODE_RELEASED, S_MASS_STORAGE_ENABLED, S_MASS_STORAGE_ENABLED],
        #[ E_SWITCH_MODE_RELEASED, S_READY, S_READY],
        [ E_SWITCH_MODE, S_READY, S_MASS_STORAGE_ENABLED],
        [ E_SWITCH_MODE, S_MASS_STORAGE_ENABLED, S_MASS_STORAGE_DISABLING],
        [ E_MASS_STORAGE_DISABLED, S_MASS_STORAGE_DISABLING, S_READY],
        [ E_CONTINUOUS_PLAYBACK_ENABLE, S_READY, S_CONTINUOUS_PLAYBACK_ENABLE],
        [ E_CONFIG_COMPLETE, S_CONTINUOUS_PLAYBACK_ENABLE, S_READY],
        [ E_CONTINUOUS_PLAYBACK_DISABLE, S_READY, S_CONTINUOUS_PLAYBACK_DISABLE],
        [ E_CONFIG_COMPLETE, S_CONTINUOUS_PLAYBACK_DISABLE, S_READY],
        [ E_TRACKING_SILENCE_ENABLE, S_READY, S_TRACKING_SILENCE_ENABLE],
        [ E_CONFIG_COMPLETE, S_TRACKING_SILENCE_ENABLE, S_READY],
        [ E_TRACKING_SILENCE_DISABLE, S_READY, S_TRACKING_SILENCE_DISABLE],
        [ E_CONFIG_COMPLETE, S_TRACKING_SILENCE_DISABLE, S_READY],
        
        
        # Playing
        [ E_PLAY_PAUSE_BUTTON, S_READY, S_PLAYING ],
        [ E_PLAY_PAUSE_BUTTON, S_PLAYING, S_PLAYING_PAUSED ],
        [ E_PLAY_PAUSE_BUTTON, S_PLAYING_PAUSED, S_PLAYING ],
        [ E_AUTO_NEXT, S_PLAYING, S_SKIP_FORWARD_WHILE_PLAYING ],
        [ E_END_OF_FILE, S_PLAYING, S_READY ],
        [ E_NO_FILE, S_SKIP_FORWARD_WHILE_PLAYING, S_READY ],
        [ E_NO_FILE, S_PLAYING, S_READY ],
        [ E_STOP_BUTTON, S_PLAYING, S_READY ],
        [ E_STOP_BUTTON, S_PLAYING_PAUSED, S_READY ],
        
        [ E_SKIP_BACK, S_PLAYING, S_SKIP_BACK_WHILE_PLAYING ],
        [ E_PREVIOUS_FILE, S_SKIP_BACK_WHILE_PLAYING, S_PLAYING ],
        [ E_NO_FILE, S_SKIP_BACK_WHILE_PLAYING, S_PLAYING ],
        [ E_SKIP_FORWARD, S_PLAYING, S_SKIP_FORWARD_WHILE_PLAYING ],
        [ E_NEXT_FILE, S_SKIP_FORWARD_WHILE_PLAYING, S_PLAYING ],
        [ E_NO_FILE, S_SKIP_FORWARD_WHILE_PLAYING, S_PLAYING ],
        
        [ E_SKIP_BACK, S_PLAYING_PAUSED, S_SKIP_BACK_WHILE_PLAYING_PAUSED ],
        [ E_PREVIOUS_FILE, S_SKIP_BACK_WHILE_PLAYING_PAUSED, S_PLAYING_PAUSED ],
        [ E_NO_FILE, S_SKIP_BACK_WHILE_PLAYING_PAUSED, S_PLAYING_PAUSED ],
        [ E_SKIP_FORWARD, S_PLAYING_PAUSED, S_SKIP_FORWARD_WHILE_PLAYING_PAUSED ],
        [ E_NEXT_FILE, S_SKIP_FORWARD_WHILE_PLAYING_PAUSED, S_PLAYING_PAUSED ],
        [ E_NO_FILE, S_SKIP_FORWARD_WHILE_PLAYING_PAUSED, S_PLAYING_PAUSED ],
        
        [ E_SEEK_BACK, S_PLAYING, S_SEEKING_BACK ],
        [ E_SEEK_BACK_RELEASED, S_SEEKING_BACK, S_PLAYING],
        [ E_SEEK_FORWARD, S_PLAYING, S_SEEKING_FORWARD ],
        [ E_SEEK_FORWARD_RELEASED, S_SEEKING_FORWARD, S_PLAYING],
        
        # Recording
        [ E_RECORD_BUTTON, S_READY, S_RECORDING ],
        [ E_RECORD_BUTTON, S_RECORDING, S_SAVING_RECORDING ],
        [ E_RECORD_BUTTON, S_RECORDING_PAUSED, S_SAVING_RECORDING ],
        [ E_STOP_BUTTON, S_RECORDING, S_SAVING_RECORDING ],
        [ E_PLAY_PAUSE_BUTTON, S_RECORDING, S_RECORDING_PAUSED ],
        [ E_PLAY_PAUSE_BUTTON, S_RECORDING_PAUSED, S_RECORDING ],
        [ E_STOP_BUTTON, S_RECORDING_PAUSED, S_SAVING_RECORDING ],
        [ E_RECORDING_SAVED, S_SAVING_RECORDING, S_READY ],
        
        # Auto-recording
        [ E_AUTO_RECORD_BUTTON, S_READY, S_WAITING_FOR_MIDI ],
        [ E_MIDI_DETECTED, S_WAITING_FOR_MIDI, S_AUTO_RECORDING ],
        [ E_MIDI_PAUSED, S_AUTO_RECORDING, S_AUTO_SAVING ],
        [ E_RECORDING_SAVED, S_AUTO_SAVING, S_WAITING_FOR_MIDI ],
        [ E_RECORDING_SAVED, S_SAVING_RECORDING, S_READY],
        [ E_STOP_BUTTON, S_AUTO_RECORDING, S_SAVING_RECORDING ],
        [ E_STOP_BUTTON, S_WAITING_FOR_MIDI, S_READY ],
        [ E_SWITCH_MODE, S_WAITING_FOR_MIDI, S_MASS_STORAGE_ENABLED],
        [ E_SWITCH_MODE, S_MASS_STORAGE_ENABLED, S_MASS_STORAGE_DISABLING],
        [ E_MASS_STORAGE_DISABLE, S_MASS_STORAGE_DISABLING, S_READY],
        [ E_MASS_STORAGE_DISABLED_FROM_AUTORECORD, S_MASS_STORAGE_DISABLING, S_WAITING_FOR_MIDI],
        [ E_AUTO_RECORD_BUTTON, S_READY, S_WAITING_FOR_MIDI]
    ]

import threading, sys, traceback

def dumpstacks(signal, frame):
    
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
                print(code.join("\n"))

import signal
signal.signal(signal.SIGQUIT, dumpstacks)


class Elephant(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    def __init__(self, name, state_machine=None, event_queue=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.event_queue = event_queue
       self.state_machine = self
       self.name = name
       
       self.active_led_managers = None
       
       self.trigger_message = None
       self.inputPort = None
       self.inputPorts = []
       self.inputPortName = None
       self.outputPort = None
       self.outputPorts = []
       self.midifile = None
       
       self.last_saved_file = None
       
       self.filemanager = None
       self.display_service = None
       
       self.playbackService = None
       self.recordingService = None
       self.midiEventService = None
       
       self.withEcho = False
       
       self.continuous_playback_enabled=cfg.ContinuousPlaybackEnabled
       self.tracking_silence_enabled=cfg.TrackingSilenceEnabled
       
       
       self.seconds_of_silence=0.0
       self.isRunning=True

       self.eth0 = None
       self.wlan0 = None
       
       if (cfg.show_interfaces):
           self.eth0 = ni.ifaddresses('eth0')
           self.wlan0 = ni.ifaddresses('wlan0')
           
       self.ipaddress = None
       
       if (not self.wlan0 == None):
           self.ipaddress = f"wlan0={self.wlan0[ni.AF_INET][0]['addr']}"
       elif (not self.eth0 == None):
           self.ipaddress = f"eth0={self.eth0[ni.AF_INET][0]['addr']}"
       else:
           self.ipaddress="ipaddress=None"
           
       self.get_input_port()
       
       self.midiClocks = []
     
    def set_indicator_for_state(self, state):
        self.logger.debug(f"########### Looking for indicator for state {state}")
        if self.active_led_managers != None:
            try:
                indicator=cfg.indicator_for_state_dict[state]
                self.logger.debug(f"Found indicator params {indicator}")
                led_name=indicator[0]
                if led_name != None:
                    led=self.active_led_managers[led_name]
                    self.logger.debug(f"Got active manager for LED {led_name}")
                    if led != None:
                        led.indicator_on(indicator[1])
            except Exception as e:
                logger.warning(f"No indicator found for state {state}, {e}")
        else:
            #print(f"No LED managers are active.")
            pass
                
    def display_status(self, pause=0):
        self.logger.debug(f"########### Entering display_status()")
        status_text = []
        status_text.append(self.state)
        
        if self.state not in [S_RECORDING, S_AUTO_RECORDING, S_WAITING_FOR_MIDI, S_MASS_STORAGE_ENABLED, S_MASS_STORAGE_DISABLING]:
            try:
                file_tuple = self.filemanager.get_current_file_tuple()
            except:
                e = sys.exc_info()[0]
                logger.info("{e}")
                file_tuple = None
            if file_tuple != None:
                seconds = "{:.1f}".format(file_tuple[1])
                status_text.append(f"{file_tuple[0]} {seconds}s")
            else:
                status_text.append("No Recordings")
        else:
            status_text.append("*********")
           
        inputCount = 0
        allInputs = "" 
        for port in self.inputPorts:
              if (inputCount > 0):
                  allInputs = allInputs + ", "
              allInputs = allInputs + port.name.split(":", 1)[0]
              inputCount = inputCount + 1
              
        status_text.append(f"{allInputs}")
        status_text.append(self.ipaddress)
        status_text.append("")
        self.display_service.display_message(status_text, pause=pause)    
    
    def display_exception(self, exception):
        status_text = []
        status_text.append(self.state)
        status_text.append(self.filemanager.get_current_filename())
        status_text.append(exception)
        #self.display_service.display_message(status_text, clear, pause)    
        self.display_service.display_message(status_text)    
        
    
    def get_last_saved_file(self):
        return self.last_saved_file
    
    def get_midi_base_directory(self):
        return cfg.midi_base_directory
    
    def set_trigger_message(self, msg):
        self.trigger_message = msg
        
    def get_trigger_message(self):
        trigger_message = self.trigger_message
        if not trigger_message is None:
            self.trigger_message = None
            
        return trigger_message
        
    
    def set_midi_file(self, file):
        self.logger.debug(f"############ SET MIDIFILE TO {file}")
        self.midifile = file
        
    def get_midi_file(self):
        return self.midifile
    
    def get_state(self):
        return self.state
    
    def close_input_port(self):
        if not self.inputPort is None:
            self.inputPort.close()
            
        self.inputPort = None
    
    def set_input_port(self, inputPort):
        self.inputPort = inputPort
        
    def get_input_port(self):
        self.logger.info("########## Entering get_input_port()")
        if self.inputPort is None:
            self.logger.info(f"########## Checking for a port to open in: {cfg.inPortNames}")
            for name in cfg.inPortNames: #mido.get_input_names():
                self.logger.info(f"########### Trying to connect to {name}")
                try:
                    port = mido.open_input(name)
                    self.inputPorts.append(port)
                    self.logger.info(f"########### Successfully connected input port={name}")
                except Exception as e:
                    print(f"######## EXCEPTION opening input={name}, {e}")
                    pass
        
        self.inputPort = MultiPort(self.inputPorts)
               
        return self.inputPort
    
    def close_output_port(self):
        ##print("########## CLOSE OUTPUTS CALLED ############")
        for port in self.outputPorts:
            port.close()
        
    
    def get_output_ports(self):
        if (not self.outputPorts):
            for name in cfg.outPortNames: #mido.get_output_names():
                self.logger.info(f"########### Opening output to {name}")
                try:
                    port = mido.open_output(name)
                    self.outputPorts.append(port)
                    self.logger.info(f"########### Successfully opened output port={name}")
                except Exception as e:
                    self.logger.info(f"######### Exception while opening output={name}, {e}")
                    pass
                
        return self.outputPorts


    def raise_event(self, event_name):
        print(f"########### RAISE EVENT CALLED WITH EVENT {event_name} ##########")
        try:
            self.event_queue.put(event_name)
        except Exception as exception:
            self.logger.exception(exception)    
    
    #
    # If we are tracking 'silence', save a file that represents
    # the total amount of 'silence' since the last save
    #
    def save_silence(self):  
        filename = f"{datetime.today().strftime('%y%m%d%H%M%S')}-S.mid"
        file_to_save=f"{cfg.midi_base_directory}/{filename}"
        self.logger.debug(f"Saving silence of {self.seconds_of_silence} to {file_to_save}")
        midifile = mido.MidiFile(filename=None, file=None, type=0, ticks_per_beat=20000) 
        track = mido.MidiTrack()
        midifile.tracks.append(track)
        ticksPerBeat = 10000
        tempo = mido.bpm2tempo(120)
        
        current_time = time.time()
        delta_time = self.seconds_of_silence
        intTime = int(mido.second2tick(delta_time, ticksPerBeat, tempo))
        msg = mido.Message('note_on', note=0, velocity=0, time=intTime)
        # print(f"Appended: {msg}")
        track.append(msg)
        midifile.save(file_to_save)
        self.seconds_of_silence=0.0
        
    def save_recording(self):
        self.logger.info(f"############# Entering save_recording ELEPHANT!")
        if self.midifile is None:
            self.logger.info(f"######## NO MIDIFILE - CANNOT SAVE!")
            return
        
        
        try:
            filename = f"{datetime.today().strftime('%y%m%d%H%M%S')}.mid"
            file_to_save=f"{cfg.midi_base_directory}/{filename}"
            self.logger.info(f"File={file_to_save}")
            self.get_midi_file().save(file_to_save) 
            self.last_saved_file = filename
            self.filemanager.refresh()
            
            self.midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
            self.track = mido.MidiTrack()
            self.midifile.tracks.append(self.track)
            self.set_midi_file(self.midifile)
            self.logger.info(f"############ MIDIFILE SET TO {self.midifile} ###########")
            self.raise_event(E_RECORDING_SAVED)
            
            # Clear output ports
            for port in self.get_output_ports():
                port.panic()
            
        except Exception as e:
            print(f"Exception while saving file! {e}")
            self.elephant.display_exception(e)
        
            
    def save_recording_old(self):
        self.logger.info(f"############# Entering save_recording")
        if self.midifile is None:
            self.logger.info(f"######## NO MIDIFILE - CANNOT SAVE!")
            return
        
        try:
            filename = f"{datetime.today().strftime('%y%m%d%H%M%S')}.mid"
            file_to_save=f"{cfg.midi_base_directory}/{filename}"
            self.logger.info(f"File={file_to_save}")
            self.midifile.save(file_to_save) 
            self.last_saved_file = filename
            self.set_midi_file(None)
            
            self.close_input_port()
            #self.close_output_port()
            self.filemanager.refresh()
            self.raise_event(E_RECORDING_SAVED)
        except Exception as e:
            self.display_exception(e)
            
    #####################################################        
    # State machine events are defined here        
    #####################################################
    def e_default(self, event_data): 
        pass
        
    def e_waiting_for_midi(self, event_data): 
        pass
        #self.midiEventService = MIDIEventService.MIDIEventService(name="MIDIEventService", 
        #                                        elephant=self)
        #self.midiEventService.start()
        
            
    def x_waiting_for_midi(self, event_data): 
        pass
        
    def e_auto_recording(self, event_data):
        self.recordingService.set_recording_start_time() 
            
    def x_auto_recording(self, event_data): 
        pass
        
    def e_auto_saving(self, event_data): 
        #self.save_recording()
        pass
    
    def x_auto_saving(self, event_data): 
        pass
    
    def e_playing(self, event_data): 
        if event_data.transition.source != S_PLAYING_PAUSED:
            self.playbackService = PlaybackService.PlaybackService(name="PlaybackService", 
                                                          elephant=self, continuous=self.continuous_playback_enabled)
            self.playbackService.start()
        else:
            self.playbackService.pause_event.set()
       
        
    def e_continuous_playback_enable(self, event_data): 
        self.continuous_playback_enabled=True
        self.raise_event(E_CONFIG_COMPLETE)
        
    def e_continuous_playback_disable(self, event_data): 
        print(event_data.transition)
        self.continuous_playback_enabled=False
        self.raise_event(E_CONFIG_COMPLETE)
        
    def e_tracking_silence_enable(self, event_data): 
        print(event_data.transition)
        self.tracking_silence_enabled=True
        self.raise_event(E_CONFIG_COMPLETE)
        
    def e_tracking_silence_disable(self, event_data): 
        print(event_data.transition)
        self.tracking_silence_enabled=False
        self.raise_event(E_CONFIG_COMPLETE)

    def x_playing(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_playing_paused(self, event_data):
        print(f"Enter {self.state}")
        self.playbackService.pause_event.clear() 

    def x_playing_paused(self, event_data): 
        #print(f"Exit {self.state}")
        pass

    def e_recording(self, event_data):
        self.recordingService.set_recording_start_time() 
        pass

    def x_recording(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_recording_paused(self, event_data):
       pass

    def x_recording_paused(self, event_data): 
        pass
        #print(f"Exit {self.state}")

    def e_saving_recording(self, event_data) : 
        #print("######## EVENT E_SAVING_RECORDING ########")
        #self.save_recording()
        pass
       

    def x_saving_recording(self, event_data) :
        pass

    def e_ready(self, event_data) :
        print(event_data.transition)
        if self.playbackService != None:
            self.playbackService = None
        load_kernel_module('g_midi')
        
    def x_ready(self, event_data) :
        pass
    
    def e_skip_back_while_ready(self, event_data): 
        file = self.filemanager.get_previous_filename()
        if file is not None:
            self.raise_event(E_PREVIOUS_FILE)
        else:
            self.raise_event(E_NO_FILE)

    def x_skip_back_while_ready(self, event_data): 
        pass
    
    def e_skip_back_while_playing(self, event_data): 
        if self.playbackService != None:
            print("Waiting for playback thread to terminate...")
            self.playbackService.event.set()
            self.playbackService.join()
            self.playbackService = None
            print("Continuing with skip...")
            
        file = self.filemanager.get_next_filename(full_path=True)
        print(f"Skipped back to file {file}")
        
        # Sleep so that the user knows that it happened..
        #time.sleep(.75)
        
        if file is not None:
            self.raise_event(E_PREVIOUS_FILE)
        else:
            self.raise_event(E_NO_FILE)
            
       

    def x_skip_back_while_playing(self, event_data): 
        pass

    def e_skip_back_while_playing_paused(self, event_data): 
        #print(event_data.transition)
        file = self.filemanager.get_previous_filename()
        
        # Sleep so that the user knows that it happened..
        #time.sleep(.75)
        
        if file is not None:
            self.raise_event(E_PREVIOUS_FILE)
        else:
            self.raise_event(E_NO_FILE)
            

    def x_skip_back_while_playing_paused(self, event_data): 
        pass
    
    def e_skip_forward_while_ready(self, event_data): 
        #print(event_data.transition)
        file = self.filemanager.get_next_filename()
        
        # Sleep so that the user knows that it happened..
        #time.sleep(.75)
        
        if file is not None:
            self.raise_event(E_NEXT_FILE)
        else:
            self.raise_event(E_NO_FILE)
            


    def x_skip_forward_while_ready(self, event_data): 
        pass
    
    def e_skip_forward_while_playing(self, event_data): 
        print(event_data.transition)
        if self.playbackService != None:
            print("Waiting for playback thread to terminate...")
            self.playbackService.event.set()
            self.playbackService.join()
            self.playbackService = None
            print("Continuing with skip...")
            
        file = self.filemanager.get_next_filename()
        print(f"Skipped forward to file {file}")
        
        # Sleep so that the user knows that it happened..
        #time.sleep(.75)
        
        if file is not None:
            self.raise_event(E_NEXT_FILE)
        else:
            self.raise_event(E_NO_FILE)
        
        
            

    def x_skip_forward_while_playing(self, event_data): 
       pass
    
    def e_skip_forward_while_playing_paused(self, event_data): 
        #print(event_data.transition)
        self.filemanager.get_next_filename()
        file = self.raise_event(E_NEXT_FILE)
        
        
        # Sleep so that the user knows that it happened..
        #time.sleep(.75)
        
        if file is not None:
            self.raise_event(E_NEXT_FILE)
        else:
            self.raise_event(E_NO_FILE)
            

    def x_skip_forward_while_playing_paused(self, event_data): 
       pass
    
    def e_seeking_forward(self, event_data): 
        #print(event_data.transition)
        pass

    def x_seeking_forward(self, event_data): 
        pass
    
    def e_seeking_back(self, event_data): 
        print(event_data.transition)

    def e_tracking_silence_enable(self, event_data): 
        print(event_data.transition)
        self.tracking_silence_enabled=True
        self.raise_event(E_CONFIG_COMPLETE)
    
    def e_tracking_silence_disable(self, event_data): 
        print(event_data.transition)
        self.tracking_silence_enabled=False
        self.raise_event(E_CONFIG_COMPLETE)
    
    def e_mass_storage_enable(self, event_data): 
        self.logger.info(f"e_mass_storage_enable: {event_data.transition}")
        load_kernel_module('g_mass_storage')
        remove_kernel_module('g_midi')
        
    def e_mass_storage_disable(self, event_data): 
        self.logger.info(f"e_mass_storage_disable: {event_data.transition}")
        load_kernel_module('g_midi')
        remove_kernel_module('g_mass_storage')
        if not cfg.ElephantModeEnabled:
            self.raise_event(E_MASS_STORAGE_DISABLED)
        else:
            self.raise_event(E_MASS_STORAGE_DISABLED_FROM_AUTORECORD)
   
    #
    # Start up threads that manage LED states if necessary.    
    def setup_led_managers(self):
        self.logger.debug("Setting up LED manager threads, if any...")
        active_mgr_list = []
        
        for manager_name in cfg.led_dict.keys():
            self.logger.debug(f"Checking {manager_name}")
            
            pins=cfg.led_dict[manager_name]
            
            if pins[0] != None or pins[1] != None:
                self.logger.debug(f"Adding LED manager {manager_name}")
                mgr_thread = MultiColorLEDManager.MultiColorLEDManager(manager_name)
                mgr_thread.start()
                mgr_tuple = (manager_name, mgr_thread)
                active_mgr_list.append(mgr_tuple)
    
        if len(active_mgr_list) > 0:
            self.active_led_managers = dict(active_mgr_list)

    def all_events_callback(self, event_data):
        self.logger.info(f"### TRANSITION LOGGING: {event_data.transition}")
        to_state=event_data.transition.dest 
        self.set_indicator_for_state(to_state)
        
    def setup_state_machine(self):
        self.display_service = DisplayService.DisplayService("Display", self)
        self.display_service.start()
        
        try:
            self.setup_led_managers()
        except Exception as e:
            self.logger.exception(f"setup_led_managers failed: {e}")
        
        self.machine = Machine(self, states=states, transitions=transitions,
                               before_state_change=self.all_events_callback, 
                               initial = S_READY, send_event=True)
        
        self.event_queue = queue.Queue(10)
    
        for plugin in cfg.eventThreadPlugins:
            self.logger.debug(f"Starting event thread using the '{plugin}' plugin")
            event_thread = EventThread.EventThread(name=f"{plugin}.events",
                                       state_machine=self,
                                       event_queue=self.event_queue,
                                       command_data_plugin_name=plugin)
            event_thread.start()
        
        self.filemanager = MidiFileManager.MidiFileManager(name="MidiFileManager", 
                                                           elephant=self)
        self.filemanager.refresh()
    
    def cleanup(self):
        for proc in self.midiClocks:
            print(f"Cleaning up clock {proc.out_port.name}")
            proc.run_flag.value = 0
            proc.join()
            print(f"Clock {proc.out_port.name} exited...")
            
        self.midiClocks = []
            
        sys.exit(0)
    
    def run(self):
        
        atexit.register(self.cleanup)
        
        self.setup_state_machine()
        
        self.display_status()
        
        self.get_output_ports()
        
        if (cfg.generateMIDIClock):
            ##print("############### STARTING MIDI CLOCKS ################")
            # Start MIDI clock
            run_code = Value('i', 1)
            bpm = Value('i',cfg.defaultMIDIClockBPM)
            for port in self.outputPorts:
                midi_clock_generator_proc = MIDIClockGenerator.MIDIClockGenerator(port, bpm, run_code)
                midi_clock_generator_proc.start()
                self.midiClocks.append(midi_clock_generator_proc)
                
        self.recordingService = RecordingService.RecordingService("ConstantRecordingService", 
                                                self, True)
        self.recordingService.start()

        ## Cleanup - exception handling etc.
        # Open up the input and output ports.  It's OK to run
        # without an output port but we must have an input port.
        
        self.set_indicator_for_state(S_READY)
        self.set_indicator_for_state(S_ELEPHANT_ONLINE)
        
        if cfg.ElephantModeEnabled:
            self.raise_event(E_AUTO_RECORD_BUTTON)
        try:
            while self.isRunning:
                trigger_method = self.event_queue.get()
                logging.debug('Getting ' + str(trigger_method)
                              + ' : ' + str(self.event_queue.qsize()) + ' items in queue')
                try:
                    self.logger.debug(f"Executing trigger method {trigger_method}")
                    getattr(self.state_machine, trigger_method)()
                    self.display_status(pause=.2)
                except Exception as exception:
                    self.logger.debug(exception)
            print("Elephant thread exiting...")
        except Exception as e:
            self.display_exception(e)


def dumpstacks(signal, frame):
        ##print("########### QUITTING ##########")
        return
        id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
        code = []
        for threadId, stack in sys._current_frames().items():
            code.append("\n# Thread: %s(%d)" % (id2name.get(threadId,""), threadId))
            for filename, lineno, name, line in traceback.extract_stack(stack):
                code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
                if line:
                    code.append("  %s" % (line.strip()))
                    print(f"\n".join(code))


def main():
    import threading, sys, traceback, logging
    import signal
    from functools import partial
    
    elephant_thread = Elephant(name='Elephant')
    
    def kill_handler(signal, frame):
        elephant_thread.cleanup()
        elephant_thread.display_service.display("Elephant Done!", clear=True, pause=1)
        sys.exit(0)
    
    signal.signal(signal.SIGQUIT, kill_handler)
    signal.signal(signal.SIGINT, kill_handler)
    
    try:
        if cfg.DEFAULT_LOG_LEVEL==logging.DEBUG:
            yappi.start()
            
        elephant_thread.start()
        elephant_thread.join()
        
    except KeyboardInterrupt:
        logger.exception("Interrupted")
        elephant_thread.isRunning=False
        elephant_thread.raise_event(E_STOP_BUTTON)
        elephant_thread.join()
        if cfg.DEFAULT_LOG_LEVEL==logging.DEBUG:
            yappi.stop()
            threads = yappi.get_thread_stats()
            for thread in threads:
                print(
                    "Function stats for (%s) (%d)" % (thread.name, thread.id)
                )  # it is the Thread.__class__.__name__
                yappi.get_func_stats(ctx_id=thread.id).print_all()
        sys.exit(0)
        
        

if __name__ == '__main__':
    logger=logging.getLogger(__name__)
    main()
    
