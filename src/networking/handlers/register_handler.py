import socket

from database.exceptions import NoRecordFoundError
from diagnostics.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket
from networking.user_record import UserRecord
from serialization.obj_codec import ObjCodec
from networking.auth_payload import AuthPayload

from hashing.sha256 import SHA256


class RegisterHandler(Handler):
    id = "register_handler"

    @staticmethod
    def handle(
        network_object: NetworkObject,
        sender: socket.socket,
        data: TimedPacket,
        logger: Logger = None,
    ):
        from networking.server import Server

        if isinstance(network_object, Server):
            if not network_object.database:
                if logger:
                    logger.warn("No database available for registration.")
                return

            user_auth: AuthPayload = data.data

            if not issubclass(type(user_auth), AuthPayload):
                if logger:
                    logger.warn("Invalid user record format.")
                return

            try:
                network_object.database.load(user_auth.name)
                if logger:
                    logger.warn(f"User {user_auth.name} already exists.")
            except NoRecordFoundError:
                hash, salt = SHA256().hash_with_salt(user_auth.password)
                user_record_save = UserRecord(
                    user_auth.name, user_auth.display_name, hash, salt
                )
                network_object.database.save(user_record_save)

                network_object.clients[sender.getpeername()].user_record = (
                    user_record_save
                )
                network_object.clients[sender.getpeername()].authenticated = True

                if logger:
                    logger.info(str(network_object.clients[sender.getpeername()]))
