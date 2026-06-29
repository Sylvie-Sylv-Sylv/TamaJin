import socket
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "src"))

import time
import threading

from logging.levels import Level
from logging.logger import Logger
from networking.packet import Packet
from networking.client import Client
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.test_handlers import PrintReplyHandler, ReplyHandler

logger = Logger()

logger.initialize(
    min_level = Level.DEBUG,
    console_output = True,
    use_colors = True
)

client = Client(AddressFamily.IPv4, Protocol.TCP, ('localhost', 4040))

client.add_handler(PrintReplyHandler)

try:
    client.connect(('localhost', 8080), logger)
    time.sleep(0.1)
    client.handle(logger)

    def periodly_send():
        while not client.is_stopping.is_set():
            message = 'Here\'s a message.'
            
            try:
                Packet(ReplyHandler.id, message).send(client.sock)
            except OSError:
                break
            
            logger.info(f'Sent: {message}')
            
            time.sleep(1)

    periodly_send_thread = threading.Thread(target = periodly_send)
    periodly_send_thread.start()

    while not client.is_stopping.is_set():
        pass
except KeyboardInterrupt:
    client.stop(logger)