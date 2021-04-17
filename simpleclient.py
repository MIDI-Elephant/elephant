#!/usr/local/bin/python3
import socket
import sys
import time
import termios as termios
import tty as tty
import readchar

# Create a TCP/IP socket

# Connect the socket to the port on the server given by the caller
server_address = (sys.argv[1], 10000)
while True:
    print(f"connecting to {server_address}") 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    try:
        while True:
            char = readchar.readchar()
            print(f"got '{char}'")
            sock.sendall(char.encode('utf-8'))

    finally:
        sock.close()
    
