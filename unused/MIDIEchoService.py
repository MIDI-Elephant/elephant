import threading
import ElephantCommon as common
import Elephant
import time as time
import mido as mido
import logging

class MIDIEchoService(threading.Thread):
    
    logger=logging.getLogger(__name__)

    def __init__(self, name, elephant):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.elephant = elephant
       
        