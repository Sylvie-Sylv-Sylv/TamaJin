import uuid

from database.record import Record


class UserRecord(Record):
    def __init__(self, username: str = None, password: str = None):
        super().__init__(str(uuid.uuid4()))
        
        self.username = username
        self.password = password