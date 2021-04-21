import sys 
import time
import transitions
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
import asyncio
from transitions import State
import readchar
import threading
import logging
import queue
import termios as termios
import tty as tty
from queue import Empty
from ElephantCommon import event_map as event_map
from ElephantCommon import held_character_translation_map as held_character_translation_map
from ElephantCommon import held_character_release_map as held_character_release_map


class TerminalReadcharThread(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    first_repeat_wait = .5
    normal_repeat_wait = .1
    total_repeat_count = 2
    
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.output_queue=queue.Queue(10)
       self.logger.debug(f"TerminalReadcharThread: self={self}, queue={self.output_queue}")
       
    def get_output_queue(self):
        return self.output_queue
       
    def myreadchar(self):
        fd = sys.stdin.fileno()
    
        old_settings = None
        try:
            old_settings = termios.tcgetattr(fd)
        except:
            pass
        try:
           if (old_settings != None):
               tty.setcbreak(sys.stdin.fileno())
           while True:
               ch = sys.stdin.read(1)
               if ch == '\n':
                   continue
               break
        finally:
            if (old_settings != None):
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def run(self):
        
        self.logger.debug("TerminalReadcharThread is running...")
        use_myreadchar = False
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            self.logger.debug("using readchar.readchar()")
        except Exception as e:
            self.logger.debug(f"Exception getting settings.. {e}")
            self.logger.debug("using myreadchar()")
            use_myreadchar = True
      
        
        while True:
            try:
                if use_myreadchar:
                    char = self.myreadchar()
                else:
                    char = readchar.readchar()
            except Exception as exception:
                self.logger.exception(f"readchar exception: {exception}")
                continue

            self.output_queue.put(char)

        return
       
       
       

    

