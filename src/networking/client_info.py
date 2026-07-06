# This class is the information of the clients stored by the server
import socket

from networking.user_record import UserRecord


class ClientInfo:
    def __init__(
        self, sock: socket.socket, user_record: UserRecord, authenticated: bool = False
    ):
        self.sock = sock
        self.user_record = user_record
        self.authenticated = authenticated

    def __str__(self):
        return f"""
(
    Socket: {str(self.sock)}
    User record: ({self.user_record.name}, {self.user_record.display_name}, {self.user_record._password_hash}, {self.user_record._salt})
    Authenticated: {str(self.authenticated)}
)
        """
