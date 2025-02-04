import threading
import queue
import time
import re
import logging
import DisplayMessage
import Elephant
import config_elephant as cfg

if cfg.use_lcd:
    try:
        import i2clcd as LCD
        cfg.use_lcd = True
        lcd = LCD.i2clcd(i2c_bus=0, i2c_addr=0x27, lcd_width=20)
        lcd.init()
        lcd.set_backlight(True)
    except:
        pass




class DisplayService(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.elephant = elephant
       self.name = name
       
       self.message_queue = queue.Queue(15)
       
  
    def camel_case_split(self, str):
        string_to_split = str.split(" ")[0]
        return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', string_to_split)
    
    def lprint(self, text, line):
            lcd.print_line(text, line)

    def display_line(self, text, clear=False, pause=0, line=0):
        if cfg.use_lcd and clear:
            lcd.clear()
       
        if cfg.use_lcd:
            self.lprint(text, line)
        
        self.logger.info(text)
            
        if pause > 0:
            time.sleep(pause)
            if cfg.use_lcd and clear:
                lcd.clear()
            

    def display(self, text, clear=False, pause=0):
        
        if cfg.use_lcd and clear:
            lcd.clear()
        
        # Convert state to individual words
        text[0] = self.camel_case_split(text[0])
        line_number = 0
        for line in text:
            if line == "" or line is None:
                continue
            if cfg.use_lcd:
                self.lprint(text[line_number], line_number)
            self.logger.info(text[line_number])
            line_number += 1
            
        if pause > 0:
            time.sleep(pause)
            if cfg.use_lcd and clear:
                lcd.clear()
            
    def display_message(self, text, clear=False, pause=0):
        message = DisplayMessage.DisplayMessage(text, clear=clear, pause=pause)
        
        try:
            self.message_queue.put_nowait(message)
        except Exception as e:
            self.logger.exception(f"Exception queueing message: {e}")
            
    def run(self):
         while True:
            message = self.message_queue.get()
            
            try:
                self.logger.debug(f"Displaying message {message}")
                self.display(message.text,
                             clear=message.clear, pause=message.pause)
            except Exception as exception:
                self.logger.exception(exception)
            