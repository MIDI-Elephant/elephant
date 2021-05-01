import threading
import ElephantCommon as common
import Elephant
import time as time
import mido as mido
import logging

class RecordingService(threading.Thread):
    
    logger=logging.getLogger(__name__)

    def __init__(self, name, elephant, auto):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.elephant = elephant
       self.name = name
       self.auto=auto
       self.silence_elapsed=0.0
     
    def midi_pause_elapsed(self, start_time): 
       if self.auto:
           self.silence_elapsed = time.time() - start_time
           #print(f"Elapsed: {elapsed}")
           return self.silence_elapsed >= Elephant.cfg.MAX_MIDI_IDLE_TIME_SECONDS
       else:
           return False 
                   
    def run(self):
        print(f"{self.name} started...")
        print(f"Auto={self.auto}")
        inPort=self.elephant.get_input_port()
        outPort=self.elephant.get_output_port()
        midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
        track = mido.MidiTrack()
        midifile.tracks.append(track)
        self.elephant.set_midi_file(midifile)
        
        ticksPerBeat = 10000
        tempo = mido.bpm2tempo(120)
        
        # First check for a trigger message that may have been left
        # because of triggering on a MIDI event
        msg = self.elephant.get_trigger_message()
        if not msg is None and common.is_channel_message(msg):
            msg.time = int(mido.second2tick(0, ticksPerBeat, tempo))
            if not (msg.type == 'note_on' and msg.velocity==127):
                outPort.send(msg)
                self.logger.debug(f"Appended message: {msg}")
                track.append(msg)

        last_time = time.time()
        start_time = time.time()
        while self.elephant.get_state() == common.S_RECORDING or self.elephant.get_state() == common.S_AUTO_RECORDING:
            start_time = time.time()
            while True:
                msg = inPort.poll()
                
                if msg is None:
                    time.sleep(.001)
                    if self.midi_pause_elapsed(start_time):
                         self.elephant.seconds_of_silence += self.silence_elapsed
                         self.elephant.raise_event(common.E_MIDI_PAUSED)
                         return
                    continue
                
                if msg.type=='note_on' and not msg.velocity==127:
                    outPort.send(msg)
                    #print(f"Sent: {msg}")
                else:
                    continue
                
                if not common.is_channel_message(msg) and self.midi_pause_elapsed(start_time):
                    self.elephant.seconds_of_silence += self.silence_elapsed
                    self.elephant.raise_event(common.E_MIDI_PAUSED)
                    return
                elif common.is_channel_message(msg):
                    break                    
        
            current_time = time.time()
            delta_time = current_time - last_time
            intTime = int(mido.second2tick(delta_time, ticksPerBeat, tempo))
            last_time = current_time
            msg.time = intTime
            self.logger.debug(f"Appended: {msg}")
            track.append(msg)
            
        self.elephant.close_output_port()
        self.elephant.close_input_port()
        #print(f"{self.name} exiting...")
        
