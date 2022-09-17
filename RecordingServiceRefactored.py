import threading
import ElephantCommon as common
import Elephant
import time as time
import mido as mido
import logging
import config_elephant as cfg

from datetime import datetime

class RecordingService(threading.Thread):
    
    logger=logging.getLogger(__name__)

    def __init__(self, name, elephant, auto):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.elephant = elephant
       self.name = name
       self.auto=auto
       self.silence_elapsed=0.0
       self.midifile = None
       self.track = None
       self.last_time = None
     
    
    def set_recording_start_time(self):
        self.last_time = time.time()
        
    def midi_pause_elapsed(self, start_time): 
       if self.auto:
           self.silence_elapsed = time.time() - start_time
           #print(f"Elapsed: {elapsed}")
           return self.silence_elapsed >= Elephant.cfg.MAX_MIDI_IDLE_TIME_SECONDS
       else:
           return False 
        
    
    def isRecording(self):
        return self.elephant.get_state() == common.S_AUTO_RECORDING or self.elephant.get_state() == common.S_RECORDING
    
    def isSavingRecording(self):
        return self.elephant.get_state() == common.S_SAVING_RECORDING or self.elephant.get_state() == common.S_AUTO_SAVING
    
    def isWaitingForMIDI(self):
        return self.elephant.get_state() == common.S_WAITING_FOR_MIDI
    
    def isAutoRecording(self):
        return self.elephant.get_state() == common.S_AUTO_RECORDING
    
    def isPlaying(self):
        return self.elephant.get_state() == common.S_PLAYING or self.elephant.get_state() == common.S_PLAYING_PAUSED
    
    def canEchoOrRecord(self):
        return not self.isPlaying()\
          and not self.isSavingRecording()
    
    def save_recording(self):
        self.logger.debug(f"############# Entering save_recording")
        if self.midifile is None:
            self.logger.info(f"######## NO MIDIFILE - CANNOT SAVE!")
            return
        
        try:
            filename = f"{datetime.today().strftime('%y%m%d%H%M%S')}.mid"
            file_to_save=f"{cfg.midi_base_directory}/{filename}"
            self.logger.info(f"File={file_to_save}")
            self.elephant.get_midi_file().save(file_to_save) 
            self.last_saved_file = filename
            self.elephant.filemanager.refresh()
            
            self.midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
            self.track = mido.MidiTrack()
            self.midifile.tracks.append(self.track)
            self.elephant.set_midi_file(self.midifile)
            self.logger.debug(f"############ MIDIFILE SET TO {self.midifile}")
            #print("########## WAITING FOR WAITING_FOR_MIDI OR READY ########")
            self.raise_event_and_wait_for_elephant_states(common.E_RECORDING_SAVED, [common.S_WAITING_FOR_MIDI, common.S_READY])
            
            
        except Exception as e:
            self.elephant.display_exception(e)
    
    
    def wait_for_elephant_states(self, states):
        
        while True:
            for state in states:
                if self.elephant.get_state() == state:
                    return
                
        sleep(.01)
    
    def raise_event_and_wait_for_elephant_states(self, event, states):
        self.elephant.raise_event(event)
        self.wait_for_elephant_states(states)
        
    
    def run(self):
        print(f"{self.name} started...")
        print(f"Auto={self.auto}")
        inPort=self.elephant.get_input_port()
        outPorts=self.elephant.get_output_ports()
        
        # Start out with a midi file/track
        self.midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
        self.track = mido.MidiTrack()
        self.midifile.tracks.append(self.track)
        print(f"##### SETTING MIDIFILE TO {self.midifile}")
        self.elephant.set_midi_file(self.midifile)
        self.logger.debug(f"############ MIDIFILE SET TO {self.midifile}")
        ticksPerBeat = 10000
        tempo = mido.bpm2tempo(120)
        
        # First check for a trigger message that may have been left
        # because of triggering on a MIDI event

        self.last_time = time.time()
        pause_check_start_time = time.time()
        while True:
            
            if (not self.canEchoOrRecord()):
                time.sleep(.001)
                continue
            
            # Top of message polling loop
            msg = inPort.poll()
            if msg is None:
                time.sleep(.001)
                if self.isAutoRecording() and self.midi_pause_elapsed(pause_check_start_time):
                     self.elephant.seconds_of_silence += self.silence_elapsed
                     self.elephant.raise_event(common.E_MIDI_PAUSED)
                continue
             
              
            pause_check_start_time = time.time()
            
            # Send the message to all current outputs
            for port in outPorts:
                port.send(msg)
                
            if (common.is_channel_message(msg)):
                print(f"Sent: {msg}")
             
            # Got a message and sent it. Now go into recording mode.    
            if (self.isWaitingForMIDI()):
                print("########### GOT MIDI! ##########")
                self.raise_event_and_wait_for_elephant_states(common.E_MIDI_DETECTED, [common.S_AUTO_RECORDING])
                print("########### NOW IN RECORDING MODE ############")
            
            if(self.isRecording()):
                current_time = time.time()
                delta_time = current_time - self.last_time
                intTime = int(mido.second2tick(delta_time, ticksPerBeat, tempo))
                self.last_time = current_time
                start_time = time.time
                msg.time = intTime
                
                print(f"Appended: {msg}")
                self.track.append(msg)
            
            
        print(f"{self.name} exiting...")