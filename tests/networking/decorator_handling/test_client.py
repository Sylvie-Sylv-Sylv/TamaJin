import socket
import sys
import os

from networking.network_object import NetworkObject


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

import time
import threading

from diagnostics.levels import Level
from diagnostics.logger import Logger
from networking.packet import Packet, TimedPacket
from networking.client import Client
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.basic.test_handlers import PrintReplyHandler, ReplyHandler

logger = Logger()

logger.initialize(min_level=Level.DEBUG, console_output=True, use_colors=True)

client = Client(AddressFamily.IPv4, Protocol.TCP)


@client.handler("print_reply_handler")
def print_reply_handler(
    self: NetworkObject, sender: socket.socket, data: TimedPacket, logger: Logger = None
):
    if logger:
        logger.info(f"Received reply: {data.data}")


try:
    client.connect(("localhost", 8080), logger)
    time.sleep(0.1)
    client.handle(logger)

    def periodly_send():
        while not client.is_stopping.is_set():
            message = "Here's a message."

            try:
                Packet(ReplyHandler.id, message).send(client.sock)
            except OSError:
                break

            logger.info(f"Sent: {message}")

            time.sleep(1)

    periodly_send_thread = threading.Thread(target=periodly_send)
    periodly_send_thread.start()

    while not client.is_stopping.is_set():
        time.sleep(0.1)
except KeyboardInterrupt:
    client.stop(logger)
