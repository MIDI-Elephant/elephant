import config_elephant
from ElephantCommon import *
import Elephant
import logging


class ElephantStatus(Object):
    def __init__(self, name, 
                 currentState=S_READY,
                 elephantModeEnabled=True,
                 continuousPlaybackEnabled=False,
                 trackingSilenceEnabled=False,
                 currentTrack=None,
                 inputPort=None,
                 outputPort=None,
                 apiHostName=None,
                 apiHostPort=None,
                 clientConnected=False):
        
        self.currentState=currentState
        self.elephantModEnabled=elephantModeEnabled,
        self.continuousPlaybackEnabled=continuousPlaybackEnabled,
        self.trackingSilenceEnabled=trackingSilenceEnabled,
        self.currentTrack=currentTrack,
        self.inputPort=inputPort,
        self.outputPort=outputPort,
        self.apiHostName=apiHostName,
        self.apiHostPort=apiHostPort,
        self.clientConnected=clientConnected
        


                 