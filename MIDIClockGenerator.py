import mido
from time import sleep, perf_counter
import threading
from multiprocessing import Value

class MIDIClockGenerator(threading.Thread):
    
    def __init__(self, out_port, bpm, run_flag):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.bpm = bpm
       self.out_port = out_port
       self.run_flag = run_flag
       
    def send_separator(self):
        pitchMessage = mido.Message('pitchwheel', channel=0, pitch=0)
        #print("Sending separator pitch message")
        for i in range(15):
            self.out_port.send(pitchMessage)
            

    def run(self):
        clock_tick = mido.Message('clock')
        print(f"Started clock generator for {self.out_port.name} ...")
        
        self.send_separator()
        
        while self.run_flag.value:
            pulse_rate = 60.0 / (self.bpm.value * 24)
            self.out_port.send(clock_tick)
            t1 = perf_counter()
            if self.bpm.value <= 3000:
                sleep(pulse_rate * 0.8)
            t2 = perf_counter()
            while (t2 - t1) < pulse_rate:
                t2 = perf_counter()
                
        print(f"Clock generator {self.out_port.name} exiting....")
        self.send_separator()
        print(f"Clock generator {self.out_port.name} cleanup complete....")
        
if __name__ == '__main__':
    midi_ports = mido.get_output_names()
    print(midi_ports)
    
    shared_bpm = Value('i', 120)
    run_code = Value('i', 1)
    outPort=mido.open_output('wavestate 1 In')
    #outPort=mido.open_output('wavestate:wavestate MIDI 1 24:0')
    #outPort=mido.open_output('MIDI Monitor (Untitled)')
    midi_clock_generator_proc = MIDIClockGenerator(outPort, shared_bpm, run_code)
    midi_clock_generator_proc.start()
    # sleep(.1)
    while run_code.value:
        bpm = input('Enter Tempo in BPM-> ')
        if bpm.isdigit():
            shared_bpm.value = int(bpm)
        else:
            run_code.value = False
    print('Shutting down process')
    midi_clock_generator_proc.join()
    print('exiting')
