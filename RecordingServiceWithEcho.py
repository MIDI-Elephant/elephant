import threading
import ElephantCommon as common
import Elephant
import time as time
import mido as mido
import logging

class RecordingServiceWithEcho(threading.Thread):
    
    logger=logging.getLogger(__name__)

    def __init__(self, name, elephant, auto):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.elephant = elephant
       self.name = name
       self.auto=auto
       self.silence_elapsed=0.0
       
       
       self.start_time=time.time()
       self.last_time=time.time()
       self.current_time=time.time()
       self.midifile = None
       self.track = None
        
       self.ticksPerBeat = 10000
       self.tempo = mido.bpm2tempo(120)
     
    def midi_pause_elapsed(self, start_time): 
       if self.auto:
           self.silence_elapsed = time.time() - self.start_time
           #print(f"Elapsed: {elapsed}")
           return self.silence_elapsed >= Elephant.cfg.MAX_MIDI_IDLE_TIME_SECONDS
       else:
           return False 
                   
    def start_recording(self):
        self.start_time=time.time()
        self.last_time=time.time()
        self.current_time=time.time()
        self.midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
        self.track = mido.MidiTrack()
        self.midifile.tracks.append(self.track)
        self.elephant.set_midi_file(self.midifile)
        
        self.ticksPerBeat = 10000
        self.tempo = mido.bpm2tempo(120)
        print(f"########### RECORDING STARTED ")
        
    def run(self):
        consumed_trigger_message = False
        
        print(f"########### {self.name} started...")
        print(f"########### Auto={self.auto}")
        inPort=self.elephant.get_input_port()
        outPort=self.elephant.get_output_port()
        
        while True:
            print(f"########## In RECORDING loop")
            start_time = time.time()
            while True:
                try:
                    msg = inPort.poll()
                except Exception as e:
                    print(f"Exception during poll: {e}")
                
                if msg is None:
                    time.sleep(.001)
                    if self.midi_pause_elapsed(start_time):
                         self.elephant.seconds_of_silence += self.silence_elapsed
                         self.elephant.raise_event(common.E_MIDI_PAUSED)
                    continue
                
                outPort.send(msg)
                print(f"Sent: {msg}")
               
                if not common.is_channel_message(msg) and self.midi_pause_elapsed(start_time):
                    self.elephant.seconds_of_silence += self.silence_elapsed
                    self.elephant.raise_event(common.E_MIDI_PAUSED)
                            
                if (self.elephant.get_state() == common.S_RECORDING or 
                    self.elephant.get_state() == common.S_AUTO_RECORDING):
                    
                    # First check for a trigger message that may have been left
                    # because of triggering on a MIDI event
                    if (not consumed_trigger_message and self.elephant.get_state() == common.S_AUTO_RECORDING):    
                        msg = self.elephant.get_trigger_message()
        
                        if not msg is None and common.is_channel_message(msg):
                            msg.time = int(mido.second2tick(0, ticksPerBeat, tempo))
                            outPort.send(msg)
                            print(f"Appended trigger message: {msg}")
                            self.track.append(msg)
                            consumed_trigger_message = True

                    self.current_time = time.time()
                    delta_time = self.current_time - self.last_time
                    intTime = int(mido.second2tick(delta_time, self.ticksPerBeat, self.tempo))
                    self.last_time = self.current_time
                    msg.time = intTime
                    self.logger.info(f"####### Appended: {msg}")
                    self.track.append(msg)
                else:
                    consumed_trigger_message = False
            
        self.elephant.close_output_port()
        self.elephant.close_input_port()
        print(f"{self.name} exiting...")
        
