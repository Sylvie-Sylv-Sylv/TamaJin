from database.record import Record


class UserRecord(Record):
    def __init__(self, name: str, display_name: str = None, password: str = None):
        super().__init__(name)
        
        self.display_name = display_name
        self._password = password
        
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, value: str):
        self._password = value