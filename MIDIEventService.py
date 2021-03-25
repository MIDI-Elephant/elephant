import threading
import ElephantCommon as common
import time as time
import mido as mido

class MIDIEventService(threading.Thread):
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.elephant = elephant

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
                
                self.elephant.set_trigger_message(msg)
                self.elephant.raise_event(common.E_MIDI_DETECTED)
                break
                
        print("MIDIEventService exiting...")
        
