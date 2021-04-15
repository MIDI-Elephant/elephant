#!/usr/local/bin/python3
import OPi.GPIO as GPIO
import sys
from time import sleep

MIDI_GREEN=16
POWER_GREEN=18
POWER_RED=8
MIDI_RED=10
MASS_STORAGE_TOGGLE=12

midi_green=('MIDI_GREEN', MIDI_GREEN)
midi_red=('MIDI_RED', MIDI_RED)
power_green=('POWER_GREEN', POWER_GREEN)
power_red=('POWER_RED', POWER_RED)

leds = [ midi_green, midi_red, power_green, power_red ]

GPIO.setboard(GPIO.ZERO)        # Orange Pi Zero board
GPIO.setmode(GPIO.BOARD)        # set up BOARD GPIO numbering

GPIO.setup(MASS_STORAGE_TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

try:
    for led in leds:
        print(f"Setting up {led[0]}")
        GPIO.setup(led[1], GPIO.OUT) 
        GPIO.output(led[1], False)

    led_state = True

    while True:
        sleep(.25)
        for led in leds:
            GPIO.output(led[1], True) 
            sleep(.05)
            GPIO.output(led[1], False) 
            sleep(.05)
            
finally:                     
    print("Finally")
    GPIO.cleanup()  


