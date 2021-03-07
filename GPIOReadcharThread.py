#!/usr/bin/python3
import OPi.GPIO as GPIO
import i2clcd as LCD
from time import sleep
import KeypadThread
import queue
import threading
import atexit


STOP_BOARD=11
PLAY_BOARD=13
RECORD_BOARD=15
AUTO_RECORD_BOARD=19
BACK_BOARD=21
FORWARD_BOARD=23
RECORD_STATUS_LED=26

STOP_GPIO=1
PLAY_GPIO=0
RECORD_GPIO=3
AUTO_RECORD_GPIO=15
BACK_GPIO=16
FORWARD_GPIO=14

board_pin_to_gpio = {
    STOP_BOARD     : STOP_GPIO,
    PLAY_BOARD     : PLAY_GPIO,
    RECORD_BOARD   : RECORD_GPIO,
    AUTO_RECORD_BOARD     : AUTO_RECORD_GPIO,
    BACK_BOARD     : BACK_GPIO,
    FORWARD_BOARD  : FORWARD_GPIO
    }

gpio_to_board_pin = {
    STOP_GPIO : STOP_BOARD,
    PLAY_GPIO : PLAY_BOARD,
    RECORD_GPIO : RECORD_BOARD,
    AUTO_RECORD_GPIO : AUTO_RECORD_BOARD,
    BACK_GPIO : BACK_BOARD,
    FORWARD_GPIO : FORWARD_BOARD
    }

all_board_pins = {
    STOP_BOARD,
    PLAY_BOARD,
    RECORD_BOARD,
    AUTO_RECORD_BOARD,
    BACK_BOARD,
    FORWARD_BOARD
    }

all_gpio_channels = {
    STOP_GPIO,
    PLAY_GPIO,
    RECORD_GPIO,
    AUTO_RECORD_GPIO,
    BACK_GPIO,
    FORWARD_GPIO
}


gpio_to_button = {
    STOP_GPIO    : "STOP",
    PLAY_GPIO    : "PLAY",
    RECORD_GPIO  : "RECORD",
    AUTO_RECORD_GPIO    : "AUTO_RECORD",
    BACK_GPIO    : "BACK",
    FORWARD_GPIO : "FORWARD"   
    }

board_pin_to_char = {
    STOP_BOARD          : "s",
    PLAY_BOARD          : "p",
    RECORD_BOARD        : "r",
    AUTO_RECORD_BOARD   : "a",
    BACK_BOARD          : "b",
    FORWARD_BOARD       : "f"   
}

char_queue=queue.Queue(10)
    
def setup_gpio():
    
    GPIO.setboard(GPIO.ZERO)        # Orange Pi Zero board
    GPIO.setmode(GPIO.BOARD)        # set up BOARD GPIO numbering
    for pin in all_board_pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_OFF) 
    
class GPIOReadcharThread(threading.Thread):
        
    def __init__(self, name):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.output_queue=char_queue
       atexit.register(self.cleanup)
     
    def get_output_queue(self):
        return self.output_queue
    
    def run(self):
        print("GPIOKeypadThread is running...")
        setup_gpio()
        sleep(1)
        while True:
            sleep(.08)
            try:
                for pin in all_board_pins:
                    if GPIO.input(pin):
                       char = board_pin_to_char[pin]
                       self.output_queue.put(char)
                       if (pin != FORWARD_BOARD and pin != BACK_BOARD):
                           while GPIO.input(pin):
                               pass
                            
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    sys.exit(0)
                else:
                    print(f"Exception in while loop: {e}")
            
            
    def cleanup(self):
        print("Cleaning up GPIO")
        GPIO.cleanup()
            
if __name__ == '__main__':
    
    gpio_keypad = GPIOReadcharThread(name="gpio")
    
    gpio_keypad.start()
    
    output_queue = gpio_keypad.get_output_queue()
    
    while True:
        char = output_queue.get()
        print(f"Got char '{char}'")
   