import threading
import logging
import Elephant
import ElephantCommon as common
import mido
import config_elephant as cfg
import time

#
# Discover new MIDI ports for devices that are plugged in etc.
#
class MIDIPortDiscoveryService(threading.Thread):
    
    
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.elephant=elephant
       self.logger=logging.getLogger(__name__)
       self.logger.info(f"{__name__} started....")
        
    def run(self):
        
        while True:
            if (self.elephant.get_state() != common.S_READY):
                time.sleep(5)
                self.logger.info(f"#### WAITING FOR READY STATE ######")
                continue
            
            self.elephant.refresh_midi_ports()
            
            time.sleep(5)
            
            
        
    
        

