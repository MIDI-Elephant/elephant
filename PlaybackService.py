import threading
import ElephantCommon as common
import Elephant
import time as time
import mido as mido
from mido import MidiFile


class PlaybackService(threading.Thread):
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.elephant = elephant
       self.name = name


    def run(self):
        print("PlaybackService started...")
        
        midifile_path=self.elephant.filemanager.get_current_filename(full_path=True)
        if midifile_path is None:
            self.elephant.raise_event(common.E_NO_FILE)
            return
        
        outPort=self.elephant.get_output_port()
        midifile = MidiFile(midifile_path)
        length = midifile.length
        
        for msg in midifile.play():
            if self.elephant.get_state() != common.S_PLAYING:
                break
            if not msg.is_meta:
                time.sleep(msg.time)
                outPort.send(msg)
                #print(f"Played: {msg}")
         
        self.elephant.close_output_port() 
        self.elephant.raise_event(common.E_END_OF_FILE)
        print("PlaybackService exiting...")
        print(f"State={self.elephant.get_state()}")
       
       
        
        
