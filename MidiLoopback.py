#!/usr/local/bin/python3
import mido as mido

#outPortName='f_midi'
outPortName='ElephantIAC'
#inPortName='Novation SL MkIII:Novation SL MkIII MIDI 1 20:0'
inPortName='Novation SL MkIII SL MkIII MIDI'


inPort=mido.open_input(inPortName)
outPort=mido.open_output(outPortName)

while True:
    for msg in inPort.iter_pending():
        outPort.send(msg) 
