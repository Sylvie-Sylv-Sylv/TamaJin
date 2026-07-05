import socket

from diagnostics.logger import Logger
from networking.network_object import NetworkObject


class Handler:
    id = None

    @staticmethod
    def handle(
        self: NetworkObject, sender: socket.socket, data: dict, logger: Logger = None
    ):
        raise NotImplementedError()
