import socket

from diagnostics.logger import Logger
from networking.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import Packet, TimedPacket


class PrintReplyHandler(Handler):
    id = "print_reply_handler"

    @staticmethod
    def handle(
        self: NetworkObject,
        sender: socket.socket,
        data: TimedPacket,
        logger: Logger = None,
    ):
        if logger:
            logger.info(f"Received reply: {data.data}")


class ReplyHandler(Handler):
    id = "reply_handler"

    @staticmethod
    def handle(
        self: NetworkObject,
        sender: socket.socket,
        data: TimedPacket,
        logger: Logger = None,
    ):
        reply = "Here's a reply."
        Packet(PrintReplyHandler.id, reply).send(sender)
        logger.info(f"Replied: {reply}")
