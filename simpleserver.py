#!/usr/local/bin/python3

import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
server_name = sys.argv[1]
server_address = (server_name, 10000)
print(f"starting up on {server_address}")

sock.bind(server_address)
sock.listen(1)

while True:
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print(f"client connected: {client_address}")
        message = ""
        while True:
            data = connection.recv(1)
            if len(data) == 0:
                break
            print(f"Data length={len(data)}")
            print(f"received: {data.decode('utf-8')}")
            #if data:
            #    connection.sendall(data)
            #else:
            #    break
    except Exception as e:
        print(f"Exception receiving: {e}")
    finally:
        print("Closing connection...")
        connection.close()
