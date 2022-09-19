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
import netifaces as netifaces
import psutil as psutil
import mido

#
# Discover new MIDI ports for devices that are plugged in etc.
#
class MIDIPortDiscoveryService(threading.Thread):
    
    logger=logging.getLogger(__name__)
    
    
    def __init__(self, name, elephant=None):
       # Call the Thread class's init function
       threading.Thread.__init__(self)
       self.name = name
       self.elephant=elephant
        
    def run(self):
        
        while True:
            sleep(10)
            currentPorts = self.elephant.get_input_ports()
            try:
                current_address = socket.gethostbyname(server_name)
                if current_address.split('.')[0] == '127':
                    self.logger.info(f"Address={current_address}. Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    break
            except Exception as e:
                self.logger.info(f"Exception while getting host address: {e}. Retrying in 3 seconds...")
                sleep(3)
        
        server_address = (current_address, 10000)
        self.logger.info(f"Set current host address={server_address}")
        self.elephant.set_ip_address(server_address[0])
        
        sock.bind(server_address)
        sock.listen(1)
        
        while True:
            self.logger.info('waiting for a connection')
            connection, client_address = sock.accept()
            try:
                self.logger.info(f"client connected: {client_address}")
                if self.elephant != None:
                    self.elephant.set_indicator_for_state(ElephantCommon.S_CLIENT_CONNECTED)
                message = ""
                while True:
                    data = connection.recv(1)
                    if len(data) == 0:
                        break
                    self.logger.debug(f"Data length={len(data)}")
                    self.logger.debug(f"received: {data.decode('utf-8')}")
                    self.output_queue.put(data.decode('utf-8'))
            except Exception as e:
                self.logger.exception(f"Exception receiving: {e}")
            finally:
                self.logger.info(f"Closing connection {client_address}")
                self.elephant.set_indicator_for_state(ElephantCommon.S_ELEPHANT_ONLINE)
                connection.close()
                      
if __name__ == '__main__':
    
    server=TCPReadcharThread('test')
    server.start()
    
    
        

