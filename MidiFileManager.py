import os
import glob
import threading
import ElephantCommon
import Elephant
import time
import pdb

# https://www.programcreek.com/python/example/90175/mido.MidiFile
#
# This class is responsible for managing midi files for
# Elephant. It takes care of the following tasks:
#
# create() - returns a file handle.
# Create a new midi file with the appropriate metadata and
# return it to the caller. The file is created with a name
# based on the current date/time. 
#
# open() - opens an existing midi file and returns a file handle.
# By default, the file is positioned at the beginning. 
#
# list_files() - list all files known by the MidiManager.
#
# get_current() - The MidiFileManager maintains a reference to the 'current'
# midi file which will be one that has previously been opened or created.
#
# skip_forward() - positions the MidiFileManager on the 'next' MidiFile in the
# current storage and sets the 'current' file to point to this file.
# This method returns a file handle to the 'next' file
#
# skip_back() - positions the MidiFileManager on the 'previous' MidiFile in the
# current storage and sets the 'current' file to point to this file.
# This method returns a file handle to the 'previous' file 
#
# seek_forward() - moves incrementally forward through the midi file events
# thereby providing a sort of 'fast forward' functionality for
# playing files.
#
# seek_back() - moves incrementally backward through the midi file events
# thereby providing a sort of 'rewind' functionality for
# playing files.
#
#

class MidiFileManager(threading.Thread):
    def __init__(self, name="MidiFileManager", elephant=None):
           # Call the Thread class's init function
           threading.Thread.__init__(self)
           self.elephant = elephant
           self.name = name
           
           self.current_file_index = 0
           self.last_file_index = 0
           self.current_list = []
     
    def refresh(self):
        self.current_list = sorted(glob.glob(f"{Elephant.midi_base_directory}/*.mid"), reverse=False)
        print(f"Base: {Elephant.midi_base_directory}")
        if len(self.current_list) > 0:
            # point at last element
            self.current_file_index = len(self.current_list) -1
            self.last_file_index = len(self.current_list) -1
        else:
            self.current_file_index = 0
            self.last_file_index = 0
            
               
    def get_current_file(self, refresh=False):
        if refresh:
            self.refresh()
        
        if len(self.current_list) == 0:
            return None
        
        if len(self.current_list) - 1 >= self.current_file_index:
            file_to_return = self.current_list[self.current_file_index]
            Elephant.display(file_to_return.split('/')[3].split(".")[0], 1)
            return file_to_return
        
        return None
            
    def get_next_file(self, refresh=False):
        if refresh:
            self.refresh()
            
        if len(self.current_list) == 0:
            return None
        
        if self.current_file_index >= 0:
            next_file_index = self.current_file_index + 1
            if next_file_index <= self.last_file_index:
                self.current_file_index = next_file_index
                return self.get_current_file()
            
        return None
    
    def get_previous_file(self, refresh=False):
        if refresh:
            self.refresh()
            
        if self.current_file_index > 0:
            previous_file_index = self.current_file_index - 1
            self.current_file_index = previous_file_index
            return self.get_current_file()
            
        
        return None
    
    def get_file_count(self, refresh=False):
        if refresh:
            self.refresh()
        if self.current_list is None:
            return 0
        
        return len(self.current_list)
    
    def run(self):
        print(f"{self.name} is running...")
        
        self.refresh()
        
        while True:
            time.sleep(100000)
        
        

                    
