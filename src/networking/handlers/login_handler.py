import socket

from database.exceptions import NoRecordFoundError
from diagnostics.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket
from networking.user_record import UserRecord
from networking.auth_payload import AuthPayload
from serialization.obj_codec import ObjCodec

from hashing.sha256 import SHA256


class LoginHandler(Handler):
    id = "login_handler"

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
                    logger.warn("No database available for login.")
                return

            user_auth: AuthPayload = data.data

            if not issubclass(type(user_auth), AuthPayload):
                if logger:
                    logger.warn("Invalid user record format.")
                return

            try:
                stored_user_record: UserRecord = network_object.database.load(
                    user_auth.name
                )

                if SHA256().verify_with_salt(
                    user_auth.password,
                    stored_user_record._password_hash,
                    stored_user_record._salt,
                ):
                    network_object.clients[sender.getpeername()].user_record = (
                        stored_user_record
                    )
                    network_object.clients[sender.getpeername()].authenticated = True
                    if logger:
                        logger.info(
                            f"Successful login for {user_auth.name} at {sender.getpeername()}."
                        )
                else:
                    if logger:
                        logger.warn(
                            f"Login failed: Incorrect password for {user_auth.name} at {sender.getpeername()}."
                        )

            except NoRecordFoundError:
                if logger:
                    logger.warn(f"Login failed: User {user_auth.name} does not exist.")
