import socket
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

from diagnostics.levels import Level
from diagnostics.logger import Logger
from networking.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import Packet
from networking.server import Server
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.basic.test_handlers import ReplyHandler

logger = Logger()

logger.initialize(min_level=Level.DEBUG, console_output=True, use_colors=True)

server = Server(AddressFamily.IPv4, Protocol.TCP, ("localhost", 8080), encoding="utf-8")

server.add_handler(ReplyHandler)

try:
    server.run(logger)

    while not server.is_stopping.is_set():
        time.sleep(0.1)
except KeyboardInterrupt:
    server.stop(logger)
