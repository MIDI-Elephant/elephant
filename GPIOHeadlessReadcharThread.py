import OPi.GPIO as GPIO
import time
import threading
import logging
import atexit
import queue
from config_elephant import *

class GPIOHeadlessReadcharThread(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    def __init__(self, name, elephant=None):
        super().__init__(daemon=True)

        self.pin = MASS_STORAGE_BOARD
        self.lock = threading.Lock()
        self.bouncetime=.01
        atexit.register(self.cleanup)
        self.output_queue=queue.Queue(50)
        self.elephant=elephant
        atexit.register(self.cleanup)
     
    def get_output_queue(self):
        return self.output_queue

    def __call__(self, *args):
        #print(f"Internal callback called with args={args}")
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
     
        char = board_pin_to_char[self.pin]
        self.logger.debug(f"Putting char '{char}' into output queue")
        self.lock.release()
        
    def cleanup(self):
        #print("Cleaning up GPIO")
        GPIO.cleanup()
        
        
if __name__ == '__main__':
    
    GPIO.setboard(GPIO.ZERO)        # Orange Pi Zero board
    GPIO.setmode(GPIO.BOARD)    
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
    
    cb = GPIOHeadlessReadcharThread('readchar')
    cb.start()
    GPIO.add_event_detect(12, GPIO.RISING, callback=cb)
    
    while True:
        time.sleep(1)
