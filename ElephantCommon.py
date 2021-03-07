E_PLAY_PAUSE_BUTTON='PlayPauseButton'
E_RECORD_BUTTON='RecordButton'
E_STOP_BUTTON='StopButton'
E_BACK_BUTTON='BackButton'
E_FORWARD_BUTTON='NextButton'
E_LOOP_BUTTON='LoopButton'

# Triggers via internal events
E_RECORDING_SAVED='RecordingSaved'
E_END_OF_TRACK='EndOfTrack'
E_PREVIOUS_TRACK='PreviousTrack'
E_NEXT_TRACK='NextTrack'
E_SKIP_FORWARD='SkipForward'
E_SKIP_BACK='SkipBack'
E_SEEK_FORWARD='SeekForward'
E_SEEK_FORWARD_RELEASED='SeekForwardReleased'
E_SEEK_BACK='SeekBack'
E_SEEK_BACK_RELEASED='SeekBackReleased'

event_map ={
    'p' : E_PLAY_PAUSE_BUTTON, 
    'r' : E_RECORD_BUTTON,
    's' : E_STOP_BUTTON,
    'b' : E_BACK_BUTTON,
    'f' : E_FORWARD_BUTTON,
    'l' : E_LOOP_BUTTON,
    'B' : E_SKIP_BACK,
    'F' : E_SKIP_FORWARD,
    '{' : E_SEEK_BACK,
    '}' : E_SEEK_FORWARD,
    '[' : E_SEEK_BACK_RELEASED,
    ']' : E_SEEK_FORWARD_RELEASED
    
    }

back_forward_to_seek_map = {
    'b' : '{',
    'f' : '}',
    }

back_forward_to_seek_release_map = {
     'b' : '[',
    'f' : ']',
    }

skip_event_map ={
    'b' : E_SKIP_BACK,
    'f' : E_SKIP_FORWARD
    }

seek_event_map = {
    'b' : E_SEEK_BACK,
    'f' : E_SEEK_FORWARD
    }

S_STOPPED='Stopped'
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


