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
import ElephantCommon

class TCPReadcharThread(threading.Thread):
    first_repeat_wait = .5
    normal_repeat_wait = .1
    total_repeat_count = 2
    
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.output_queue=queue.Queue(10)
       self.elephant=elephant
       
    def get_output_queue(self):
        return self.output_queue
    
    def run(self):
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the address given on the command line
        server_name = socket.gethostname()
        server_address = (server_name, 10000)
        print(f"starting up on {server_address}")
        
        sock.bind(server_address)
        sock.listen(1)
        
        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            try:
                print(f"client connected: {client_address}")
                if self.elephant != None:
                    self.elephant.set_indicator_for_state(ElephantCommon.S_CLIENT_CONNECTED)
                message = ""
                while True:
                    data = connection.recv(1)
                    if len(data) == 0:
                        break
                    print(f"Data length={len(data)}")
                    print(f"received: {data.decode('utf-8')}")
                    self.output_queue.put(data.decode('utf-8'))
            except Exception as e:
                print(f"Exception receiving: {e}")
            finally:
                print("Closing connection...")
                self.elephant.set_indicator_for_state(ElephantCommon.S_ELEPHANT_ONLINE)
                connection.close()
                      
if __name__ == '__main__':
    
    server=TCPReadcharThread('test')
    server.start()
    
    
        

