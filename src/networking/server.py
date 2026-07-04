import copy
import socket
import select
import threading
import time
from multipledispatch import dispatch

from database.database import Database
from diagnostics.logger import Logger
from networking.address_family import AddressFamily
from networking.client_info import ClientInfo
from networking.handlers.handler import Handler
from networking.handlers.register_handler import RegisterHandler
from networking.network_object import NetworkObject
from networking.protocol import Protocol
from networking.packet import Packet, TimedPacket
from networking.handlers.client_quit_handler import ClientQuitHandler
from networking.handlers.server_quit_handler import ServerQuitHandler
from networking.user_record import UserRecord


class Server(NetworkObject):
    def __init__(
        self,
        address_family: AddressFamily,
        protocol: Protocol,
        address: tuple,
        encoding: str = "utf-8",
        database: Database = None
    ):
        self.is_stopping = threading.Event()

        self.sock = socket.socket(address_family.value, protocol.value)
        self.sock.bind(address)
        
        self.clients: dict[tuple, ClientInfo] = {}

        self.encoding = encoding

        self.handlers: dict[str, Handler] = {}
        self.add_handler(ClientQuitHandler)
        self.add_handler(RegisterHandler)
        
        self.database = database

    def add_client(self, sock: socket.socket, user_record: UserRecord):
        if sock.fileno() == -1:
            return

        self.clients[sock.getpeername()] = ClientInfo(sock, user_record)

    def remove_client(self, address: tuple):
        client_info = self.clients.pop(address, None)
        sock = client_info.sock

        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            sock.close()

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

    def _handle(self, logger: Logger = None):
        readables, _, _ = select.select(
            [client.sock for client in self.clients.values()] + [self.sock], [], [], 0.5
        )

        for client in readables:
            # ------------------------
            # Handle bad client
            # ------------------------
            if client.fileno() == -1:
                if client not in self.clients.values():
                    continue

                self.remove_client(client.getpeername())

            # ------------------------
            # Handle new connections
            # ------------------------
            if client == self.sock:
                self._auth_and_acc(logger)
                continue

            # ------------------------
            # Receive data
            # ------------------------
            data = TimedPacket.recv(client, self.encoding)

            if data.handler in self.handlers:
                self.handlers[data.handler].handle(self, client, data, logger)

    def _auth_and_acc(self, logger: Logger = None):
        client, address = self.sock.accept()

        self.add_client(client, ClientInfo(client, None, False))

        # Send the encoding
        Packet(None, self.encoding).send(client, self.encoding)

        logger.info(
            f"Authenticated client {address} and sent the encoding used for this network: {self.encoding}."
        )

    def _run(self, hard_reset_database: bool = False, logger: Logger = None):
        self.database.connect()
        if not hard_reset_database: self.database.initialize()
        else: self.database.hard_reset()
        
        self.sock.listen()

        logger.info(f"Begin listening for connections.")

        while not self.is_stopping.is_set():
            self._handle(logger)

    def run(self, hard_reset_database: bool = False, logger: Logger = None):
        self.run_thread = threading.Thread(target=self._run, kwargs={'hard_reset_database': hard_reset_database, 'logger': logger})
        self.run_thread.start()

    def stop(self, logger: Logger = None):
        self.is_stopping.set()

        self.run_thread.join()

        for client_info in self.clients.values():
            client = client_info.sock
            try:
                Packet(ServerQuitHandler.id, None).send(client, encoding=self.encoding)
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

        time.sleep(0.1)

        for address in copy.deepcopy(list(self.clients.keys())):
            self.remove_client(address)

        self.sock.close()

        if logger:
            logger.info("Shutting down...")
