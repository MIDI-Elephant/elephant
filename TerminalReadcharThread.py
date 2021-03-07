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
from queue import Empty
import ElephantThread
import EventThread
import KeypadThread
from ElephantCommon import event_map as event_map
from ElephantCommon import back_forward_to_seek_map as back_forward_to_seek_map
from ElephantCommon import back_forward_to_seek_release_map as back_forward_to_seek_release_map

char_queue=queue.Queue(5)

class TerminalReadcharThread(threading.Thread):
    def __init__(self, name):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.output_queue=char_queue
       
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
        
        print("TerminalReadcharThread is running...")
        use_myreadchar = False
        try:
            old_settings = termios.tcgetattr(fd)
            print("using readchar.readchar()")
        except:
            print("using myreadchar()")
            use_myreadchar = True
        
        use_myreadchar = False
      
        while True:
            try:
                if use_myreadchar:
                    char = self.myreadchar()
                else:
                    char = readchar.readchar()
            except Exception as exception:
                print("readchar exception")
                print(exception)
                continue

            self.output_queue.put(char)

        return
       
       
       

    

