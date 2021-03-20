import threading
import ElephantCommon as elephant
import mido as mido

#outPortName='f_midi'
outPortName='ElephantIAC'
#inPortName='Novation SL MkIII:Novation SL MkIII MIDI 1 20:0'
inPortName='Novation SL MkIII SL MkIII MIDI'
#theOnlyMIDIFile = 'usb_share/midifile.mid'
theOnlyMIDIFile = '/Users/edward/midifile.mid'

class RecordingService(threading.Thread):
    def __init__(self, name, state_machine=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.state_machine = state_machine
       self.name = name


    def run(self):
        print("RecordingService started...")
        start_time = time.time()
        inPort=mido.open_input(inPortName)
        outPort=mido.open_output(outPortName)
        midifile = mido.MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
        track = mido.MidiTrack()
        midifile.tracks.append(track)

        while self.state_machine.state == elephant.S_RECORDING:
            for msg in inPort.iter_pending():
#                outPort.send(msg)
                if (msg.type == 'note_on' or
                    msg.type == 'note_off'):
                    track.append(msg)
                
        print("RecordingService exiting...")
        
        print("Saving recording...")
        midifile.save(theOnlyMIDIFile) 
        outPort.reset()
        outPort.close()
        inPort.close()   
        
