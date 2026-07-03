import socket
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

from logging.levels import Level
from logging.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import Packet, TimedPacket
from networking.server import Server
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.basic.test_handlers import ReplyHandler

logger = Logger()

logger.initialize(
    min_level = Level.DEBUG,
    console_output = True,
    use_colors = True
)

server = Server(AddressFamily.IPv4, Protocol.TCP, ('localhost', 8080), encoding = 'utf-8')

@server.handler('reply_handler')
def reply_handler(self: NetworkObject, sender: socket.socket, data: TimedPacket, logger: Logger = None):
    reply = 'Here\'s a reply.'
    Packet('print_reply_handler', reply).send(sender)
    logger.info(f'Replied: {reply}')

try:
    server.run(logger)
    
    while not server.is_stopping.is_set():
        time.sleep(0.1)
except KeyboardInterrupt:
    server.stop(logger)