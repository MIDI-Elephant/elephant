import sys 
import time
import transitions
from transitions.extensions.asyncio import AsyncMachine
from transitions import Machine
import asyncio
from transitions import State
import readchar
import threading
import logging
import queue
import termios as termios
import tty as tty
import socket
from queue import Empty
import KeypadThread
from ElephantCommon import event_map as event_map
from ElephantCommon import held_character_translation_map as held_character_translation_map
from ElephantCommon import held_character_release_map as held_character_release_map

class TCPReadcharThread(threading.Thread):
    def __init__(self, name):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.output_queue=queue.Queue(10)
       
    def get_output_queue(self):
        return self.output_queue
    
    def run(self):
        
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the address given on the command line
        server_name = socket.gethostname()
        server_address = (server_name, 10000)
        print(f"starting up on {server_address}")
        
        while True:
            try:
                sock.bind(server_address)
                break
            except Exception as e:
                print(f"Exception binding {server_address} - retrying in 10s");
                time.sleep(10)
            
                 
        sock.listen(1)
        
        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            print(f"client connected: {client_address}")
            message = ""
            while True:
                try:
                    data = connection.recv(1)
                    if len(data) == 0:
                        break
                    print(f"Data length={len(data)}")
                    print(f"{self.name} received: {data.decode('utf-8')}")
                    self.output_queue.put(data.decode('utf-8'))
                    print(f"{self.name} queued: {data.decode('utf-8')}")
                except Exception as e:
                    print(f"Exception receiving: {e}")
                    break
                finally:
                    print("Closing connection...")
                    connection.close()
                      
       

