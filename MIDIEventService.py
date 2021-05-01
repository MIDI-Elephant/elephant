import threading
import ElephantCommon as common
import time as time
import mido as mido
from datetime import datetime

class MIDIEventService(threading.Thread):
    def __init__(self, name, elephant=None, tracking_silence=False):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.elephant = elephant
       self.wait_start_time=time.time()
       
    
    def run(self):
        print("MIDIEventService started...")
        inPort=self.elephant.get_input_port()
        while self.elephant.get_state() == common.S_WAITING_FOR_MIDI:
                msg = inPort.poll()
                
                if msg is None:
                    time.sleep(.001)
                    continue
                
                if not common.is_channel_message(msg):
                    continue
                
                if msg.type == 'control_change' and msg.control == 11:
                    print(f"Filtering: {msg}")
                    continue
                
                if msg.velocity==127 and msg.note==60:
                    print(f"Filtering: {msg}")
                    continue

                self.elephant.set_trigger_message(msg)
                print(f"Trigger message: {msg}")
                
                if self.elephant.tracking_silence_enabled:
                    self.elephant.seconds_of_silence += time.time() - self.wait_start_time
                    self.elephant.save_silence()
                
                self.elephant.raise_event(common.E_MIDI_DETECTED)
                break
                
        print("MIDIEventService exiting...")
        
