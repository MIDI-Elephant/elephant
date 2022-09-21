import mido

def play_file(output, filename, print_messages):
    midi_file = MidiFile(filename) 

    print('Playing {}.'.format(midi_file.filename))
    length = midi_file.length
    print('Song length: {} minutes, {} seconds.'.format(
            int(length / 60),
            int(length % 60)))
    print('Tracks:')
    for i, track in enumerate(midi_file.tracks):
        print('  {:2d}: {!r}'.format(i, track.name.strip()))

    for message in midi_file.play(meta_messages=True):
        if print_messages:
            sys.stdout.write(repr(message) + '\n')
            sys.stdout.flush()

        if isinstance(message, Message):
            output.send(message)
        elif message.type == 'set_tempo':
            print('Tempo changed to {:.1f} BPM.'.format(
                tempo2bpm(message.tempo)))

    print()
    
class SaveMIDI:
    def __init__(self):
        self.isrecording = False
        self.is_playing_midi = {}
        self.start_time = time.time()              
        
    def start_recording(self):
        self.mid = MidiFile(None, None, 0, 20000) #10000 is a ticks_per_beat value
        self.track = MidiTrack()
        self.mid.tracks.append(self.track)                
        self.isrecording = True
        menu.render_message("Recording started", "", 1000)
        self.restart_time()        
        self.messages_to_save = []  
                
    def cancel_recording(self):
        self.isrecording = False
        menu.render_message("Recording canceled", "", 1500)
        
    def add_track(self, status, note, velocity, time_value):
        self.messages_to_save.append(["note", time_value, status, note, velocity]) 
  
    def add_control_change(self, status, channel, control, value, time_value):
        self.messages_to_save.append(["control_change", time_value, status, channel, control, value])        

    def save(self, filename):
        for message in self.messages_to_save:            
            try:
                time_delay = message[1] - previous_message_time                
            except:
                time_delay = 0
            previous_message_time = message[1]

            if(message[0] == "note"):
                self.track.append(Message(message[2], note=int(message[3]), velocity=int(message[4]), time=int(time_delay*40000)))
            else:                
                self.track.append(Message(message[2], channel=int(message[3]), control=int(message[4]),  value=int(message[5]), time=int(time_delay*40000)))
            self.last_note_time = message[1]

        self.messages_to_save = []    
        self.isrecording = False
        self.mid.save('Songs/'+filename+'.mid')        
        menu.render_message("File saved", filename+".mid", 1500)
        
    def restart_time(self):
        self.start_time = time.time()



def play_midi(song_path):
    midiports.pending_queue.append(mido.Message('note_on'))
    
    if song_path in  saving.is_playing_midi.keys():
        menu.render_message(song_path, "Already playing", 2000)
        return
    
    saving.is_playing_midi.clear()
    
    saving.is_playing_midi[song_path] = True
    menu.render_message("Playing: ", song_path, 2000)
    saving.t = threading.currentThread()    

    output_time_last = 0
    delay_debt = 0;
    try:   
        mid = mido.MidiFile("Songs/"+song_path)
        fastColorWipe(ledstrip.strip, True)
        #length = mid.length        
        t0 = False        
        for message in mid:
            if song_path in saving.is_playing_midi.keys():
                if(t0 == False):
                    t0 = time.time()
                    output_time_start = time.time()            
                output_time_last = time.time() - output_time_start
                delay_temp = message.time - output_time_last
                delay = message.time - output_time_last - float(0.003) + delay_debt
                if(delay > 0):
                    time.sleep(delay)
                    delay_debt = 0
                else:
                    delay_debt += delay_temp
                output_time_start = time.time()                   
            
                if not message.is_meta:
                    midiports.playport.send(message)
                    midiports.pending_queue.append(message.copy(time=0))
                
            else:                
                break
        #print('play time: {:.2f} s (expected {:.2f})'.format(
                #time.time() - t0, length))
        #saving.is_playing_midi = False
    except:
        menu.render_message(song_path, "Can't play this file", 2000)   