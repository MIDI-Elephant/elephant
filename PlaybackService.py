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
        
        if self.elephant.get_last_saved_file() is None:
            Elephant.display("Nothing to play...")
            self.elephant.raise_event(common.E_NO_TRACK)
            return
        
        outPort=self.elephant.get_output_port()
        midifile_path=f"{self.elephant.get_midi_base_directory()}/{self.elephant.get_last_saved_file()}"
        midifile = MidiFile(midifile_path)
        Elephant.display(f"Playing {self.elephant.get_last_saved_file()}")
        
        for msg in midifile.play():
            if self.elephant.get_state() != common.S_PLAYING:
                break
            if not msg.is_meta:
                time.sleep(msg.time)
                outPort.send(msg)
                            
        print("PlaybackService exiting...")
        self.elephant.raise_event(common.E_END_OF_TRACK)
        
        
