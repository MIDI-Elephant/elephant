import os
import sys
from time import sleep
import serial

#serialPort = serial.Serial ("/dev/tty.Elephant-SPPDev", 115200) #Open port with baud rate

bytestream = bytearray()


while(1):
    try:
        #while (serialPort.inWaiting() == 0):
        #    sleep(.01)

        for char in bytes("abc\n", 'utf8'):
            #bytestream.append(serialPort.read())
            bytestream.append(char)
            
        printbytes = bytearray()
        for byte in bytestream:
            printbytes.append(byte)
            if byte == ord('\n'):
                print(printbytes.decode('utf8'))
                printbytes = bytearray()

    except Exception as e:
        print(f"Got exception while reading: {e}")
