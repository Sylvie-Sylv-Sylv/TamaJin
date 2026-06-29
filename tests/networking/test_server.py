import socket
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

from logging.levels import Level
from logging.logger import Logger
from networking.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import Packet
from networking.server import Server
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.test_handlers import ReplyHandler

logger = Logger()

logger.initialize(
    min_level = Level.DEBUG,
    console_output = True,
    use_colors = True
)

server = Server(AddressFamily.IPv4, Protocol.TCP, ('localhost', 8080), encoding = 'utf-8')

server.add_handler(ReplyHandler)

try:
    server.listen(logger)

    while True:
        pass
except KeyboardInterrupt:
    server.stop(logger)