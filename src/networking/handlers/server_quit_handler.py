import socket

from diagnostics.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket


class ServerQuitHandler(Handler):
    id = "server_quit_handler"

    @staticmethod
    def handle(
        network_object: NetworkObject,
        sender: socket.socket,
        data: TimedPacket,
        logger: Logger = None,
    ):
        from networking.client import Client

        if isinstance(network_object, Client):
            logger.info("Server stopped, client is quitting.")
            network_object.stop(logger)
