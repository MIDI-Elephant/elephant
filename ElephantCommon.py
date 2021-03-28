
#
# Some configuration values
#
MAX_MIDI_IDLE_TIME_SECONDS=10

#
# The following are the events generated by
# button presses.
#
E_PLAY_PAUSE_BUTTON='E_PlayPauseButton'
E_RECORD_BUTTON='E_RecordButton'
E_STOP_BUTTON='E_StopButton'
E_BACK_BUTTON='E_BackButton'
E_FORWARD_BUTTON='E_NextButton'
E_AUTO_RECORD_BUTTON='E_AutoRecordButton'

# 
# The following events are generated by internal code
#
E_RECORDING_SAVED='E_RecordingSaved'
E_END_OF_TRACK='E_EndOfTrack'
E_NO_TRACK='E_No_Track'
E_PREVIOUS_TRACK='E_PreviousTrack'
E_NEXT_TRACK='E_NextTrack'
E_SKIP_FORWARD='E_SkipForward'
E_SKIP_BACK='E_SkipBack'
E_SEEK_FORWARD='E_SeekForward'
E_SEEK_FORWARD_RELEASED='E_SeekForwardReleased'
E_SEEK_BACK='E_SeekBack'
E_SEEK_BACK_RELEASED='E_SeekBackReleased'
E_MIDI_DETECTED='E_MIDIDetected'
E_MIDI_PAUSED='E_MIDIPaused'
# Switch 'Gadget' between MIDI and Mass Storage
E_SWITCH_MODE='E_SwitchMode'
E_SWITCH_MODE_RELEASED='E_SwitchModeReleased'

#
# This table maps characters that can be typed
# on a keyboard to events generated by button presses
# or events that are derived by button presses.
event_map ={
    'p' : E_PLAY_PAUSE_BUTTON, 
    'r' : E_RECORD_BUTTON,
    's' : E_STOP_BUTTON,
    'b' : E_BACK_BUTTON,
    'f' : E_FORWARD_BUTTON,
    'a' : E_AUTO_RECORD_BUTTON,
    'B' : E_SKIP_BACK,
    'F' : E_SKIP_FORWARD,
    '{' : E_SEEK_BACK,
    '}' : E_SEEK_FORWARD,
    '[' : E_SEEK_BACK_RELEASED,
    ']' : E_SEEK_FORWARD_RELEASED,
    'X' : E_SWITCH_MODE,
    'x' : E_SWITCH_MODE_RELEASED
    }

characters_that_can_repeat = {
    'b', 'f', 's'
    }

held_character_translation_map = {
    'b' : '{',
    'f' : '}',
    's' : 'X',
    'x' : 'X'
    }

held_character_release_map = {
     'b' : '[',
    'f' : ']',
    # No release character for 's'
    's' : ' '
    }

non_held_character_translation_map = {
    'b' : 'B',
    'f' : 'F',
    's' : 's'  
    }

#
# These are all of the states related to interactions
# with the Elephant transport
#
S_STOPPED='ElephantReady!'
S_PLAYING='Playing'
S_PLAYING_PAUSED='PlayingPaused'
S_RECORDING='Recording'
S_RECORDING_PAUSED='RecordingPaused'
S_SAVING_RECORDING='SavingRecording'
S_SKIP_BACK_WHILE_STOPPED='SkipBackWhileStopped'
S_SKIP_FORWARD_WHILE_STOPPED='SkipForwardWhileStopped'
S_SKIP_BACK_WHILE_PLAYING='SkipBackWhilePlaying'
S_SKIP_FORWARD_WHILE_PLAYING_PAUSED='SkipForwardWhilePlayingPaused'
S_SKIP_BACK_WHILE_PLAYING_PAUSED='SkipBackWhilePlayingPaused'
S_SKIP_FORWARD_WHILE_PLAYING='SkipForwardWhilePlaying'
S_SEEKING_FORWARD='SeekingForward'
S_SEEKING_BACK='SeekingBack'
S_WAITING_FOR_MIDI='WaitingForMIDI'
S_AUTO_RECORDING='AutoRecording'
S_AUTO_SAVING='AutoSaving'
S_MASS_STORAGE_MANAGEMENT='MassStorageManagement'

def is_channel_message(msg):
    return (msg.type in midi_channel_messages.keys())

midi_channel_messages = {
    'note_off' : 'channel note velocity',
    'note_on' : 'channel note velocity',
    'polytouch' : 'channel note value',
    'control_change' : 'channel control value',
    'program_change' : 'channel program',
    'aftertouch' : 'channel value',
    'pitchwheel' : 'channel pitch'
}


