import socket

from database.exceptions import NoRecordFoundError
from diagnostics.logger import Logger
from networking.handlers.handler import Handler
from networking.network_object import NetworkObject
from networking.packet import TimedPacket
from networking.user_record import UserRecord
from serialization.obj_codec import ObjCodec


class RegisterHandler(Handler):
    id = 'register_handler'
    
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
                if logger: logger.warn('No database available for registration.')
                return
            
            user_record: UserRecord = data.data
            
            if not issubclass(type(user_record), UserRecord):
                if logger: logger.warn('Invalid user record format.')
                return
            
            try: 
                network_object.database.load(user_record.name)
                if logger: logger.warn(f"User {user_record.name} already exists.")
            except NoRecordFoundError:
                network_object.database.save(user_record)
                
                network_object.clients[sender.getpeername()].user_record = user_record
                network_object.clients[sender.getpeername()].authenticated = True
                
                if logger: logger.info(str(network_object.clients[sender.getpeername()]))