#!/usr/local/bin/python3
import OPi.GPIO as GPIO
import sys
import time
from time import sleep

MIDI_GREEN=16
MIDI_RED=10
STATUS_GREEN=18
STATUS_RED=8

MASS_STORAGE_TOGGLE=12

color_dict = {
                'green' : (.0083, 0), 
                'red' : (0, .0083), 
                'yellow' : (.00680, .00200),
                'orange' : (.00275, .00623) 
                }
led_dict = {
            'midi' : (MIDI_GREEN, MIDI_RED),
            'elephant' : (STATUS_GREEN, STATUS_RED)
            }

IDX_GREEN_LED_INTERVAL=0
IDX_RED_LED_INTERVAL=1

IDX_GREEN_LED_PIN=0
IDX_RED_LED_PIN=1




leds = [ midi_green, midi_red, STATUS_GREEN, STATUS_RED ]

GPIO.setboard(GPIO.ZERO)        # Orange Pi Zero board
GPIO.setmode(GPIO.BOARD)        # set up BOARD GPIO numbering

GPIO.setup(MASS_STORAGE_TOGGLE, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

def led_on(led_name, color, seconds=2):
    
    led = led_dict[led_name]
    color_params = color_dict[color]
    
    green_interval = color_params[GREEN_LED_INTERVAL]
    red_interval = color_params[RED_LED_INTERVAL]
    
    green_pin = led[GREEN_LED_PIN]
    red_pin = led[RED_LED_PIN]
    
    start_time = time.perf_counter()
    
    while True:
        GPIO.output(green_pin, True)
        sleep(green_interval)
        GPIO.output(green_pin, False)
        GPIO.output(red_pin, True)
        sleep(red_interval)
        GPIO.output(red_pin, False)
        
        if seconds > 0 and (time.perf_counter() - start_time >= seconds):
            break

    
    


def blend(seconds, red_led, green_led):

    adjust_value = .00003
    green_time = 0;
    red_time = .0083

    Forward = True

    start_time = time.perf_counter()
    while True:
        GPIO.output(green_led, True)
        sleep(green_time)
        GPIO.output(green_led, False)
        GPIO.output(red_led, True)
        sleep(red_time)
        GPIO.output(red_led, False)
        if time.perf_counter() - start_time >= seconds:
            break

        if Forward:
            green_time += adjust_value 
            red_time -=  adjust_value

            if green_time >= .0083:
                Forward = False
        else:
            red_time += adjust_value 
            green_time -=  adjust_value

            if red_time >= .0083:
                Forward = True

        red_time = max(red_time, 0)
        green_time = max(green_time, 0)

def blend_test():
    try:
        for led in leds:
            print(f"Setting up {led[0]}")
            GPIO.setup(led[1], GPIO.OUT) 
            GPIO.output(led[1], False)
    
        led_state = True
        
        iterations = 0
        max_iterations = 1
    
        while iterations < max_iterations:
            for led in leds:
                GPIO.output(led[1], True)
                sleep(2)
                GPIO.output(led[1], False)
    
            blend(5, MIDI_GREEN, MIDI_RED)
            blend(5, STATUS_GREEN, STATUS_RED)
            
            iterations += 1
            
                
    finally:                     
        print("Finally")
    GPIO.cleanup()  

#blend_test()

def color_test():
    for led in leds:
            print(f"Setting up {led[0]}")
            GPIO.setup(led[1], GPIO.OUT) 
            GPIO.output(led[1], False)
            
    while True:
        for color in color_dict.keys():
            for led_name in led_dict.keys():
                print(f"{led_name}:{color}")
                led_on(led_name, color, seconds=1)
            
            
color_test()

