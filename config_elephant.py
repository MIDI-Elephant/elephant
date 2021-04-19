#!/usr/bin/python3

import sys
import getopt
from ElephantCommon import *

try:
    print(f"Already configured for platform {__platform__}")
except Exception as e:
    print("First time configuration!")
    __platform__='headless'
    
    # Pop first arg which is executable name
    sys.argv.pop(0)
    
    try:
        opts, args = getopt.getopt(sys.argv,"p:",["platform="])
        for opt, arg in opts:
            if opt in ("-p", "--platform"):
                __platform__=arg
    except getopt.GetoptError:
        print(f"{argv[0]} --platform=[headless|dev|mac]")
        print(f"No platform provided, continuing with default=headless")
    
   
       
    
    print(f"Configuring Elephant for platform '{__platform__}'")
    
    if __platform__ == "headless":
    
        AutoRecordEnabled=False
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = False
        use_gpio = False
        use_kmod = True
        
        inPortNames=['Novation SL MkIII:Novation SL MkIII MIDI 1 24:0',
                     'UM-ONE:UM-ONE MIDI 1 24:0', 'MIDI9/QRS PNOScan MIDI 1']
        outPortName='f_midi'
        midi_base_directory= '/mnt/usb_share'
            
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        MIDI_GREEN=16
        MIDI_RED=10
        
        STATUS_GREEN=18
        STATUS_RED=8
        
       
        MASS_STORAGE_TOGGLE=12
       
       
        
        
    elif __platform__ == "dev":
        
        AutoRecordEnabled=False
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = True
        use_gpio = True
        use_kmod = True
        
        inPortNames=['Novation SL MkIII:Novation SL MkIII MIDI 1 24:0',
                     'UM-ONE:UM-ONE MIDI 1 24:0', 'MIDI9/QRS PNOScan MIDI 1']
        outPortName='f_midi'
        
        midi_base_directory= '/mnt/usb_share'   
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        MIDI_RED=26 # solid-red = recording, flashing-red = listening for midi
        MIDI_GREEN=None  
        STATUS_GREEN=None 
        STATUS_RED=None
        
    elif __platform__ == "mac":
        
        AutoRecordEnabled=False
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = False
        use_gpio = False
        use_kmod = False
        
        inPortNames=['Novation SL MkIII:Novation SL MkIII MIDI 1 24:0',
                     'UM-ONE:UM-ONE MIDI 1 24:0', 'MIDI9/QRS PNOScan MIDI 1',
                     'VMPK Output', 'iRig MIDI 2']
        
        outPortName='ElephantIAC'
        midi_base_directory= '/mnt/usb_share'   
       
       
        inPortNames=['VMPK Output', 'iRig MIDI 2']
        midi_base_directory= '/Users/edward/MIDI'
        max_path_elements=4
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        MIDI_RED=None 
        MIDI_GREEN=None  
        STATUS_GREEN=None 
        STATUS_RED=None
    
    else:
        print(f"Unsupported platform: {__platform__}")
        sys.exit(2)
        
    RECORD_STATUS='record'
    PLAY_STATUS='play'
    ELEPHANT_ONLINE='elephant_online'
    MASS_STORAGE='mass_storage'
        
    led_manager_params = [(RECORD_STATUS, MIDI_RED), 
                          (PLAY_STATUS, MIDI_GREEN), 
                          (ELEPHANT_ONLINE, STATUS_GREEN),
                          (MASS_STORAGE, STATUS_RED)]


DEFAULT_BLINK_DELAY=.75

color_dict = {
                'green' : (.0083, 0), 
                'red' : (0, .0083), 
                'yellow' : (.00680, .00200),
                'orange' : (.00275, .00623) 
                }

MIDI_LED='midi'
ELEPHANT_LED='elephant'

led_dict = {
            MIDI_LED : (MIDI_GREEN, MIDI_RED),
            ELEPHANT_LED : (STATUS_GREEN, STATUS_RED)
}




c_green='green'
c_green_blink='green:b'
c_green_flash='green:f'
c_red='red'
c_red_blink='red:b'
c_red_flash='red:f'
c_yellow='yellow'
c_yellow_blink='yellow:b'
c_yellow_flash='yellow:f'
c_orange='orange'
c_orange_blink='orange:b'
c_orange_flash='orange:f'

all_led_colors = [ c_green, c_red, c_yellow, c_orange ]


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

#
# Definitions for 'indicators' for different states

indicator_for_state_dict = {
    S_RECORDING : (MIDI_LED, c_red),
    S_RECORDING_PAUSED : (MIDI_LED, c_red_blink),
    S_PLAYING : (MIDI_LED, c_green),
    S_PLAYING_PAUSED :(MIDI_LED, c_green_blink),
    S_WAITING_FOR_MIDI : (MIDI_LED, c_red_blink),
    S_AUTO_RECORDING : (MIDI_LED, c_red),
    S_SAVING_RECORDING : (MIDI_LED, c_orange),
    S_AUTO_SAVING : (MIDI_LED, c_orange),
    S_READY : (MIDI_LED, c_yellow),
    S_MIDI_ERROR : (MIDI_LED, c_red_flash),
    S_MASS_STORAGE_MANAGEMENT : (ELEPHANT_LED, c_orange_blink),
    S_ELEPHANT_ONLINE : (ELEPHANT_LED, c_green),
    S_CLIENT_CONNECTED : (ELEPHANT_LED, c_green_blink),
    S_ELEPHANT_ERROR : (ELEPHANT_LED, c_red_flash)
}


        
print(f"Platform '{__platform__}' was successfully configured.")
    
        
    

