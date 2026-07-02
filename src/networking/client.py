import socket
import threading

from logging.logger import Logger
from networking.address_family import AddressFamily
from networking.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import Packet, TimedPacket
from networking.protocol import Protocol
from networking.client_quit_handler import ClientQuitHandler
from networking.server_quit_handler import ServerQuitHandler
from networking.user_record import UserRecord


class Client(NetworkObject):
    def __init__(self, address_family: AddressFamily, protocol: Protocol, user_record: UserRecord):
        self.is_stopping = threading.Event()

        self.sock = socket.socket(address_family.value, protocol.value)

        self.handlers: dict[str, Handler] = {}
        self.add_handler(ServerQuitHandler)

    # Decorator for handler
    def handler(self, id: str):
        def wrapper(func: callable):
            class NewHandler(Handler):
                id = id

                @staticmethod
                def handle(
                    self: NetworkObject,
                    sender: socket.socket,
                    data: TimedPacket,
                    logger: Logger = None,
                ):
                    func(self, sender, data, logger)

            self.handlers[id] = NewHandler

        return wrapper

    def add_handler(self, handler: Handler):
        self.handlers[handler.id] = handler

    def _connect(self, address: tuple, logger: Logger = None):
        self.sock.connect(address)
        self.encoding = TimedPacket.recv(self.sock).data
        if logger:
            logger.info("Connected")

    def connect(self, address: tuple, logger: Logger = None):
        self.connect_thread = threading.Thread(
            target=self._connect, kwargs={"address": address, "logger": logger}
        )
        self.connect_thread.daemon = True
        self.connect_thread.start()

    def _handle(self, logger: Logger = None):
        while not self.is_stopping.is_set():
            try:
                data = TimedPacket.recv(self.sock, self.encoding)
            except OSError:
                break

            if data.handler in self.handlers:
                self.handlers[data.handler].handle(self, self, data, logger)

    def handle(self, logger: Logger = None):
        self.handle_thread = threading.Thread(
            target=self._handle, kwargs={"logger": logger}
        )
        self.handle_thread.start()

    def stop(self, logger: Logger = None):
        self.is_stopping.set()

        # Send client quit handler if the otherside is still available
        try:
            Packet(ClientQuitHandler.id, None).send(self.sock, encoding=self.encoding)
            self.sock.shutdown(socket.SHUT_WR)
        except OSError:
            pass

        self.sock.close()

        if logger:
            logger.info("Shutting down...")
