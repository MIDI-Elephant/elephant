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
