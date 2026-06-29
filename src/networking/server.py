import socket
import threading

from logging.logger import Logger
from networking.address_family import AddressFamily
from networking.handler import Handler
from networking.network_object import NetworkObject
from networking.protocol import Protocol
from networking.packet import Packet, TimedPacket
from networking.client import EncodingHandler
from networking.client_quit_handler import ClientQuitHandler
from networking.server_quit_handler import ServerQuitHandler

class Server(NetworkObject):
    def __init__(self, address_family: AddressFamily, protocol: Protocol, address: tuple, encoding: str = 'utf-8'):
        self.sock = socket.socket(
            address_family.value,
            protocol.value
        )
        
        self.sock.bind(address)
        
        self.encoding = encoding
        
        self.clients: dict[tuple, socket.socket] = {}
        self.handle_threads = []
        
        self.handlers: dict[str, Handler] = {}
        
        self.add_handler(ClientQuitHandler)
        
    def remove_client(self, address: tuple):
        self.clients.pop(address)
    
    def add_handler(self, handler: Handler):
        self.handlers[handler.id] = handler
        
    def _handle_client(self, client: socket.socket, logger: Logger = None):
        while True:
            try:
                data = TimedPacket.recv(client, self.encoding)
            except OSError:
                break
            
            if data.handler in self.handlers:
                self.handlers[data.handler].handle(self, client, data, logger)
    
    def _listen_and_authenticate(self, logger: Logger = None):
        logger.info(f'Begin listening for connections.')
        
        self.sock.listen()
        
        while True:
            try:
                client, address = self.sock.accept()
            except OSError:
                break
            
            self.clients[address] = client

            # Send the encoding
            Packet(EncodingHandler.id, self.encoding).send(client, self.encoding)
            
            handle_thread = threading.Thread(target = self._handle_client, kwargs = {'client': client, 'logger': logger})
            handle_thread.daemon = True
            
            self.handle_threads.append(handle_thread)
            
            handle_thread.start()
            
            logger.info(f'Authenticated client {address} and sent the encoding used for this network: {self.encoding}.')
    
    def listen(self, logger = None):
        self.listen_thread = threading.Thread(target = self._listen_and_authenticate, kwargs = {'logger': logger})
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
    def stop(self, logger: Logger = None):
        for client in self.clients.values():
            Packet(ServerQuitHandler.id, None).send(client, encoding = self.encoding)
            client.shutdown(socket.SHUT_WR)
        self.sock.close()
        if logger: logger.info('Shutting down...')