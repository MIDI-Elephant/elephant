#!/usr/bin/python3

import sys
import getopt

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
        
        PLAY_STATUS_LED=16  # solid-green = playing, flashing-green = playing paused
        ELEPHANT_ONLINE_LED=18 # solid-green = ready, flashing-green = app connected
        MASS_STORAGE_ENABLED_LED=8
        RECORD_STATUS_LED=10 # solid-red = recording, flashing-red = listening for midi
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
        
        RECORD_STATUS_LED=26 # solid-red = recording, flashing-red = listening for midi
        PLAY_STATUS_LED=None  
        ELEPHANT_ONLINE_LED=None 
        MASS_STORAGE_ENABLED_LED=None
        
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
        
        RECORD_STATUS_LED=None 
        PLAY_STATUS_LED=None  
        ELEPHANT_ONLINE_LED=None 
        MASS_STORAGE_ENABLED_LED=None
    
    else:
        print(f"Unsupported platform: {__platform__}")
        sys.exit(2)
        
    RECORD_STATUS='record'
    PLAY_STATUS='play'
    ELEPHANT_ONLINE='elephant_online'
    MASS_STORAGE='mass_storage'
        
    led_manager_params = [(RECORD_STATUS, RECORD_STATUS_LED), 
                          (PLAY_STATUS, PLAY_STATUS_LED), 
                          (ELEPHANT_ONLINE, ELEPHANT_ONLINE_LED),
                          (MASS_STORAGE, MASS_STORAGE_ENABLED_LED)]
        
        
print(f"Platform '{__platform__}' was successfully configured.")
    
        
    


