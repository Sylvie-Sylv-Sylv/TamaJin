import socket

from database.exceptions import NoRecordFoundError
from diagnostics.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket
from networking.user_record import UserRecord
from serialization.obj_codec import ObjCodec


class LoginHandler(Handler):
    id = 'login_handler'
    
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
                if logger: logger.warn('No database available for login.')
                return
            
            user_record: UserRecord = data.data
            
            if not issubclass(type(user_record), UserRecord):
                if logger: logger.warn('Invalid user record format.')
                return
            
            try: 
                stored_user_record: UserRecord = network_object.database.load(user_record.name)
                
                if stored_user_record.password == user_record.password:
                    network_object.clients[sender.getpeername()].user_record = user_record
                    network_object.clients[sender.getpeername()].authenticated = True
                    if logger: logger.info(f"Successful login for {user_record.name} at {sender.getpeername()}.")
                else:
                    if logger: logger.warn(f"Login failed: Incorrect password for {user_record.name} at {sender.getpeername()}.")
                
            except NoRecordFoundError:
                if logger: logger.warn(f'Login failed: User {user_record.name} does not exist.')