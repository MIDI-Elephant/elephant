import os
import glob
from ElephantCommon import *
import Elephant
import time
import pdb
import traceback
from mido import MidiFile


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

class MidiFileManager():
    def __init__(self, name="MidiFileManager", elephant=None):
           self.elephant = elephant
           self.name = name
           
           self.current_file_index = 0
           self.last_file_index = 0
           self.current_list = []
           self.current_tuples = []
     
    def get_full_path(self, filename):
        return f"{Elephant.cfg.midi_base_directory}/{filename}.mid"
        
    def refresh(self):
        self.current_list = []
        self.current_tuples = []
        glob_list = glob.glob(f"{Elephant.cfg.midi_base_directory}/*.mid")
        
        #print(f"glob_list={glob_list}")
        
        self.current_list = sorted(glob.glob(f"{Elephant.cfg.midi_base_directory}/*.mid"), reverse=False)
        
        #print(self.current_list)
        
        for midifile_path in self.current_list:
            try:
                midifile = MidiFile(midifile_path)
                new_file_tuple = tuple((midifile_path, midifile.length))
                print(f"Appending: {new_file_tuple}")
                self.current_tuples.append(new_file_tuple)
            except Exception as e:
                print(f"Exception opening {midifile_path}: {e}")
                os.remove(midifile_path)
                print(f"Removed invalid file: {midifile_path}")
        
        if len(self.current_list) > 0:
            # point at last element
            self.current_file_index = len(self.current_list) -1
            self.last_file_index = len(self.current_list) -1
        else:
            self.current_file_index = 0
            self.last_file_index = 0  
    
    def get_current_file_tuple(self, refresh=False, full_path=False):
        if refresh:
            self.refresh()
             
        if len(self.current_list) == 0:
            return None
        
        if len(self.current_list) - 1 >= self.current_file_index:
            tuple_to_return = self.current_tuples[self.current_file_index]
            if full_path:
                return tuple_to_return
            else:
                new_tuple = tuple((f"{tuple_to_return[0].split('/')[Elephant.cfg.max_path_elements].split('.')[0]}", tuple_to_return[1]))
                return new_tuple
        
        return None
    
    
    def get_current_filename(self, refresh=False, full_path=False):
        if refresh:
            self.refresh()
        
        if len(self.current_list) == 0:
            return None
        
        if len(self.current_list) - 1 >= self.current_file_index:
            file_to_return = self.current_list[self.current_file_index]
            if full_path:
                return file_to_return
            else:
                return f"{file_to_return.split('/')[Elephant.cfg.max_path_elements].split('.')[0]}"
        
        return None
            
    def get_next_filename(self, refresh=False, full_path=False):
        if refresh:
            self.refresh()
            
        if len(self.current_list) == 0:
            return None
        
        if self.current_file_index >= 0:
            next_file_index = self.current_file_index + 1
            if next_file_index <= self.last_file_index:
                self.current_file_index = next_file_index
                return self.get_current_filename(full_path=full_path)
          
        return None      
    
    def get_previous_filename(self, refresh=False, full_path=False):
        if refresh:
            self.refresh()
            
        if self.current_file_index > 0:
            previous_file_index = self.current_file_index - 1
            self.current_file_index = previous_file_index
            return self.get_current_filename(full_path=full_path)
            
        
        return None
    
    def get_file_count(self, refresh=False):
        if refresh:
            self.refresh()
        if self.current_list is None:
            return 0
        
        return len(self.current_list)
    
    
    def save_recording(self, new_filename):
        if self.midifile is None:
            return
        
        try:
            filename = f"{datetime.today().strftime('%y%m%d%H%M%S')}.mid"
            file_to_save=f"{Elephant.cfg.midi_base_directory}/{filename}"
            #print(f"File={file_to_save}")
            self.midifile.save(file_to_save) 
            self.last_saved_file = filename
            self.set_midi_file(None)
            
            self.close_input_port()
            self.close_output_port()
            self.filemanager.refresh()
            self.raise_event(E_RECORDING_SAVED)
        except Exception as e:
            self.display_exception(e)
    

                    
