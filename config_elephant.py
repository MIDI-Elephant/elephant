#!/usr/bin/python3

import sys
import getopt
import logging

DEFAULT_LOG_LEVEL=logging.INFO

logging.basicConfig(format='%(levelname)s:%(name)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=DEFAULT_LOG_LEVEL)
from ElephantCommon import *

logger=logging.getLogger('Configuration')

show_interfaces = False
midiEcho = True

try:
    logger.info(f"Already configured for platform {__platform__}")
except Exception as e:
    logger.info("First time configuration!")
    __platform__='headless'
    
    # Pop first arg which is executable name
    sys.argv.pop(0)
    
    try:
        opts, args = getopt.getopt(sys.argv,"p:",["platform="])
        for opt, arg in opts:
            if opt in ("-p", "--platform"):
                __platform__=arg
    except getopt.GetoptError:
        logger.error(f"{argv[0]} --platform=[headless|dev|mac]")
        logger.error(f"No platform provided, continuing with default=headless")
       
    
    logger.info(f"Configuring Elephant for platform '{__platform__}'")
    
    #
    # All platforms can get input from the terminal and via  a TCP connection
    eventThreadPlugins=['TerminalReadcharThread', 'TCPReadcharThread']
    
    if __platform__ == "headless":
        
        #eventThreadPlugins=['TCPReadcharThread', 'GPIOReadcharThread', 'TerminalReadcharThread']
        eventThreadPlugins=['TCPReadcharThread', 'GPIOHeadlessReadcharThread']
            
        ElephantModeEnabled=True
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = False
        use_gpio = True
        use_kmod = True
        
        
        inPortNames=['Nord Grand:Nord Grand MIDI 1 24:0',
                    'Novation SL MkIII:Novation SL MkIII MIDI 1',
                     'UM-ONE:UM-ONE MIDI 1', 'MIDI9/QRS PNOScan MIDI 1']
        outPortName='f_midi'
        midi_base_directory= '/mnt/usb_share'
            
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        STATUS_GREEN=16
        STATUS_RED=10
        
        MIDI_GREEN=18
        MIDI_RED=8
        
        #
        # These constants refer to the pin numbers on the 
        # Orange Pi Zero LTS that correspond to buttons
        # on a given hardware device.  Only the 'dev' and 'headless'
        # platforms for Elephant have buttons so these do not
        # need to be defined for other platforms
        #
        MASS_STORAGE_TOGGLE=12 # Pin used by button on headless platform to toggle mass storage
        
        STOP_BOARD=None
        PLAY_BOARD=None
        RECORD_BOARD=None
        AUTO_RECORD_BOARD=None
        BACK_BOARD=None
        FORWARD_BOARD=None
        MASS_STORAGE_BOARD=12
        
    elif __platform__ == "desktop":
        
        show_interfaces = True
        eventThreadPlugins=['GPIOReadcharThread', 'TCPReadcharThread']
        
        ElephantModeEnabled=False
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = True
        use_gpio = True
        use_kmod = True
        
        inPortNames=['MPK mini 3:MPK mini 3 MIDI 1 28:0']
        outPortNames=['f_midi', 'wavestate:wavestate MIDI 1 24:0']
        #outPortName='Nord Grand:Nord Grand MIDI 1 24:0'
        
        midi_base_directory= '/mnt/usb_share'   
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        MIDI_RED=26 # solid-red = recording, blinking-red = listening for midi
                    # flashing red = saving recording
        MIDI_GREEN=None  
        STATUS_GREEN=None 
        STATUS_RED=None
        
        #
        # These constants refer to the pin numbers on the 
        # Orange Pi Zero LTS that correspond to buttons
        # on a given hardware device.  Only the 'dev' and 'headless'
        # platforms for Elephant have buttons so these do not
        # need to be defined for other platforms
        #
        STOP_BOARD=11
        PLAY_BOARD=13
        RECORD_BOARD=15
        AUTO_RECORD_BOARD=19
        BACK_BOARD=21
        FORWARD_BOARD=23
        MASS_STORAGE_BOARD=None
    
    elif __platform__ == "dev":
        
        midiEcho = False
        show_interfaces = True
        eventThreadPlugins=['GPIOReadcharThread', 'TCPReadcharThread']
        
        ElephantModeEnabled=False
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = True
        use_gpio = True
        use_kmod = True
        
        inPortNames=['Nord Grand:Nord Grand MIDI 1 24:0']
        #outPortName='f_midi'
        outPortNames=['Nord Grand:Nord Grand MIDI 1 24:0', 'wavestate:wavestate MIDI 1 28:0']
        
        midi_base_directory= '/mnt/usb_share'   
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        MIDI_RED=26 # solid-red = recording, blinking-red = listening for midi
                    # flashing red = saving recording
        MIDI_GREEN=None  
        STATUS_GREEN=None 
        STATUS_RED=None
        
        #
        # These constants refer to the pin numbers on the 
        # Orange Pi Zero LTS that correspond to buttons
        # on a given hardware device.  Only the 'dev' and 'headless'
        # platforms for Elephant have buttons so these do not
        # need to be defined for other platforms
        #
        STOP_BOARD=11
        PLAY_BOARD=13
        RECORD_BOARD=15
        AUTO_RECORD_BOARD=19
        BACK_BOARD=21
        FORWARD_BOARD=23
        MASS_STORAGE_BOARD=None
    
        
    elif __platform__ == "mac":
        
        #eventThreadPlugins=['TerminalReadcharThread', 'TCPReadcharThread']
        eventThreadPlugins=['TerminalReadcharThread']
        
        ElephantModeEnabled=False
        Headless=True
        ContinuousPlaybackEnabled=False
        TrackingSilenceEnabled=False
        
        use_lcd = False
        use_gpio = False
        use_kmod = False
        

        inPortNames=['MPK mini 3', 'VMPK Output']
        
        #inPortNames=['Nord Grand MIDI Output', 'Nord Grand:Nord Grand MIDI 1 24:0',
        #              'Novation SL MkIII:Novation SL MkIII MIDI 1',
        #             'UM-ONE:UM-ONE MIDI 1', 'MIDI9/QRS PNOScan MIDI 1',
        #             'VMPK Output', 'iRig MIDI 2']
        
        #outPortName='ElephantIAC'
        outPortNames=['ElephantIAC', 'wavestate 1 In']
        #outPortName2='Network Session 3'
        #midi_base_directory= '/mnt/usb_share'   
       
       
        #inPortNames=['VMPK Output', 'iRig MIDI 2']
        midi_base_directory= '/Users/edward/MIDI'
        max_path_elements=4
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
        MIDI_RED=None 
        MIDI_GREEN=None  
        STATUS_GREEN=None 
        STATUS_RED=None
        
        STOP_BOARD=None
        PLAY_BOARD=None
        RECORD_BOARD=None
        AUTO_RECORD_BOARD=None
        BACK_BOARD=None
        FORWARD_BOARD=None
        MASS_STORAGE_BOARD=None
    
    else:
        logger.fatal(f"Unsupported platform: {__platform__}")
        sys.exit(2)
        
    RECORD_STATUS='record'
    PLAY_STATUS='play'
    ELEPHANT_ONLINE='elephant_online'
    MASS_STORAGE='mass_storage'
        
    led_manager_params = [(RECORD_STATUS, MIDI_RED), 
                          (PLAY_STATUS, MIDI_GREEN), 
                          (ELEPHANT_ONLINE, STATUS_GREEN),
                          (MASS_STORAGE, STATUS_RED)]


all_board_pins = {
    STOP_BOARD,
    PLAY_BOARD,
    RECORD_BOARD,
    AUTO_RECORD_BOARD,
    BACK_BOARD,
    FORWARD_BOARD,
    MASS_STORAGE_BOARD
    }


board_pin_to_char = {
    STOP_BOARD          : "s",
    PLAY_BOARD          : "p",
    RECORD_BOARD        : "r",
    AUTO_RECORD_BOARD   : "a",
    BACK_BOARD          : "b",
    FORWARD_BOARD       : "f",
    MASS_STORAGE_BOARD  : "X"  
}

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
                c_yellow : (.00380, .00500),
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
    S_PLAYING : (MIDI_LED, c_yellow),
    S_PLAYING_PAUSED :(MIDI_LED, c_yellow_blink),
    S_WAITING_FOR_MIDI : (MIDI_LED, c_red_blink),
    S_AUTO_RECORDING : (MIDI_LED, c_red),
    S_SAVING_RECORDING : (MIDI_LED, c_red_flash),
    S_AUTO_SAVING : (MIDI_LED, c_orange),
    S_MASS_STORAGE_ENABLED : (MIDI_LED, c_orange_flash),
    S_READY : (MIDI_LED, c_green),
    S_MIDI_ERROR : (MIDI_LED, c_red_flash),
    S_ELEPHANT_ONLINE : (ELEPHANT_LED, c_green),
    S_CLIENT_CONNECTED : (ELEPHANT_LED, c_green_flash),
    S_ELEPHANT_ERROR : (ELEPHANT_LED, c_red_flash)
}


        
logger.info(f"Platform '{__platform__}' was successfully configured.")
    
        
    


