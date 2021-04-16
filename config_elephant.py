#!/usr/bin/python3

import sys
import getopt

try:
    print(f"Already configured for platform {__platform__}")
except Exception as e:
    print("First time configuration!")
    __platform__='NOTCONFIGURED'
    
    # Pop first arg which is executable name
    sys.argv.pop(0)
    
    try:
        opts, args = getopt.getopt(sys.argv,"p:",["platform="])
    except getopt.GetoptError:
        print(f"{argv[0]} --platform=[headless|dev|mac]")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-p", "--platform"):
            __platform__=arg
       
    
    print(f"Configuring Elephant for platform '{__platform__}'")
    
    if __platform__ == "headless":
    
        AutoRecordEnabled=False
        Headless=True
        
        use_lcd = False
        use_gpio = False
        use_kmod = True
        
        inPortNames=['Novation SL MkIII:Novation SL MkIII MIDI 1 24:0',
                     'UM-ONE:UM-ONE MIDI 1 24:0', 'MIDI9/QRS PNOScan MIDI 1']
        outPortName='f_midi'
        midi_base_directory= '/mnt/usb_share'
            
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
    elif __platform__ == "dev":
        
        AutoRecordEnabled=False
        Headless=False
        
        use_lcd = True
        use_gpio = True
        use_kmod = True
        
        inPortNames=['Novation SL MkIII:Novation SL MkIII MIDI 1 24:0',
                     'UM-ONE:UM-ONE MIDI 1 24:0', 'MIDI9/QRS PNOScan MIDI 1']
        outPortName='f_midi'
        
        midi_base_directory= '/mnt/usb_share'   
        max_path_elements=3
        
        MAX_MIDI_IDLE_TIME_SECONDS=10
        
    elif __platform__ == "mac":
        
        AutoRecordEnabled=False
        Headless=False
        
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
    
    else:
        print(f"Unsupported platform: {__platform__}")
        sys.exit(2)
        
        
print(f"Platform '{__platform__}' was successfully configured.")
    
        
    


