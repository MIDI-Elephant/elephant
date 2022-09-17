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
       
    def isRecording(self):
        return self.elephant.get_state() == common.S_AUTO_RECORDING or self.elephant.get_state() == common.S_RECORDING
                   
    def run(self):
        print(f"{self.name} started...")
        print(f"Auto={self.auto}")
        inPort=self.elephant.get_input_port()
        outPorts=self.elephant.get_output_ports()
        midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
        track = mido.MidiTrack()
        midifile.tracks.append(track)
        self.elephant.set_midi_file(midifile)
        self.logger.debug(f"############ MIDIFILE SET TO {midifile}")
        
        ticksPerBeat = 10000
        tempo = mido.bpm2tempo(120)
        
        # First check for a trigger message that may have been left
        # because of triggering on a MIDI event

        last_time = time.time()
        start_time = time.time()
        while True:
            
            if (self.elephant.get_state() == common.S_AUTO_RECORDING):
                msg = self.elephant.get_trigger_message()
                if not msg is None and common.is_channel_message(msg):
                    msg.time = int(mido.second2tick(0, ticksPerBeat, tempo))
                    if not (msg.type == 'note_on' and msg.velocity==127 and msg.note==60):
                        for port in outPorts:
                            port.send(msg)
                        self.logger.debug(f"Appended message: {msg}")
                        track.append(msg)
            
            msg = inPort.poll()
            
            if msg is None:
                time.sleep(.001)
                if self.midi_pause_elapsed(start_time):
                     self.elephant.seconds_of_silence += self.silence_elapsed
                     self.elephant.raise_event(common.E_MIDI_PAUSED)
                     return
                continue
            
            for port in outPorts:
                port.send(msg)
                
            if (common.is_channel_message(msg)):
                print(f"Sent: {msg}")
            
            
            current_time = time.time()
            delta_time = current_time - last_time
            intTime = int(mido.second2tick(delta_time, ticksPerBeat, tempo))
            last_time = current_time
            msg.time = intTime
            
            if common.is_channel_message(msg) and self.isRecording():
                print(f"Appended: {msg}")
                track.append(msg)
            
            if not common.is_channel_message(msg) and self.midi_pause_elapsed(start_time) and \
            self.elephant.get_state() == common.S_AUTO_RECORDING:
                self.elephant.seconds_of_silence += self.silence_elapsed
                self.elephant.raise_event(common.E_MIDI_PAUSED)
                while (self.elephant.get_state() == common.E_MIDI_PAUSED and not self.elephant.get_state() == common.S_RECORDING):
                    sleep(.05) 
                start_time = time.time()
            
        #self.elephant.close_output_ports()
        self.elephant.close_input_port()
        print(f"{self.name} exiting...")