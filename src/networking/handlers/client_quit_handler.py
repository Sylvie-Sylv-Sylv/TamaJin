import socket

from logging.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket


class ClientQuitHandler(Handler):
    id = "client_quit_handler"

    @staticmethod
    def handle(
        network_object: NetworkObject,
        sender: socket.socket,
        data: TimedPacket,
        logger: Logger = None,
    ):
        from networking.server import Server

        if isinstance(network_object, Server):
            logger.info(f"Client {sender.getpeername()} disconnected.")
            network_object.remove_client(sender.getpeername())

        sender.close()
