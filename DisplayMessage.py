

class DisplayMessage():

    def __init__(self, text, clear=True, pause=0, line=0):
       self.text = text
       self.clear = clear
       self.pause = pause
       self.line = line
       
    def __str__(self):
        return f"{self.text}, clear={self.clear}, pause={self.pause}"
    
