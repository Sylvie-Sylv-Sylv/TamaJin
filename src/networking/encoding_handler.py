import socket

from logging.logger import Logger
from networking.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket


class EncodingHandler(Handler):
    id = 'encoding_handler'
    
    @staticmethod
    def handle(network_object: NetworkObject, sender: socket.socket, data: TimedPacket, logger: Logger = None):
        network_object.encoding = data.data