import mido
import time as time
from datetime import datetime

input=mido.open_input('MIDI9/QRS PNOScan:MIDI9/QRS PNOScan MIDI 1')
#input=mido.open_input('UM-ONE:UM-ONE MIDI 1 24:0')
lastMessageTime=time.perf_counter()
flurryCount=0
while True:
    for msg in input.iter_pending():
        print(msg)
        flurryCount+= 1
        currentMessageTime=time.perf_counter()
        if currentMessageTime - lastMessageTime > 1:
            print(datetime.now())
            print(f"Last flurry of {flurryCount} notes  was {currentMessageTime-lastMessageTime} seconds ago")
            lastMessageTime=time.perf_counter() 
            flurryCount=0

        time.sleep(.001)

