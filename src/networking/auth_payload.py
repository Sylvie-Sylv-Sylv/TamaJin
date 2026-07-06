from database.record import Record

class AuthPayload(Record):
    def __init__(self, name: str, password: str, display_name: str = ""):
        super().__init__(name)
        
        self.name = name
        self.password = password
        self.display_name = display_name
