#!/usr/local/bin/python3

# import required libraries 
from pydub import AudioSegment 
from pydub.playback import play 

# Import an audio file 
# Format parameter only 
# for readability 
wav_file = AudioSegment.from_file(file = "elephant.wav", format = "wav") 

# Play the audio file 
play(wav_file)

