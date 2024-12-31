import threading
from threading import Event
import ElephantCommon as common
import Elephant
import time as time
import mido as mido
import logging
from multiprocessing import Process, Value

from mido import MidiFile


class PlaybackService(threading.Thread):
    def __init__(self, name, elephant=None, continuous=False):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       
       self.logger=logging.getLogger(__name__)
       
       self.elephant = elephant
       self.name = name
       
       self.continuous = continuous
       self.terminate = False
       self.event = Event()
       self.pause_event = Event()
       self.run_clock = Value('i', True)
       

    def run(self):
        self.logger.info(f"############# PlaybackService started, continuous={self.continuous}")
        
        midifile_path=self.elephant.filemanager.get_current_filename(full_path=True)
        if midifile_path is None:
            self.elephant.raise_event(common.E_NO_FILE)
            return
        
        midifile = MidiFile(midifile_path)
        length = midifile.length
        outPorts = self.elephant.get_output_ports()
        
        for msg in midifile.play():
            if self.elephant.get_state() != common.S_PLAYING and self.elephant.get_state() != common.S_PLAYING_PAUSED:
                break
            
            while self.elephant.get_state() == common.S_PLAYING_PAUSED:
                self.pause_event.wait(timeout=.1)
            
            if not msg.is_meta:
                self.event.wait(msg.time)
                if self.event.is_set():
                    break
                for port in outPorts:
                    port.send(msg)
                #print(f"Played: {msg}")
         
        # clear output ports
        if True:
            for port in outPorts:
                port.panic()
        
        if not self.continuous:
            self.elephant.raise_event(common.E_END_OF_FILE)
        else:
            self.elephant.raise_event(common.E_AUTO_NEXT)
          
        self.stop_clocks()  
        print(f"PlaybackService exiting, terminate={self.terminate}")
        print(f"State={self.elephant.get_state()}")
       
    def start_clock(self, port):
         shared_bpm = Value('i', 120)
         midi_clock_generator_proc = Process(target=clockGen.midi_clock_generator, args=(port, shared_bpm, self.run_clock))
         midi_clock_generator_proc.start()
             
    def stop_clocks(self):
        self.run_clock.value = False
           
      
        
