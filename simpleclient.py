#!/usr/local/bin/python3
import socket
import sys
import time

# Create a TCP/IP socket

# Connect the socket to the port on the server given by the caller
server_address = (sys.argv[1], 10000)
while True:
    print(f"connecting to {server_address}") 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)

    try:
        message = 'This is the message.  It will be repeated.'
        print(f"sending: '{message}' repeatedly...") 
        sock.sendall(message.encode('utf-8')) == 0
        amount_expected = len(message)
        amount_received = 0
        new_data = "" 
        while amount_received < amount_expected:
            data = sock.recv(16)
            new_data += data.decode('utf-8')
            amount_received += len(data)

        print(f"received: {new_data}")

    finally:
        sock.close()
    
    time.sleep(2)
