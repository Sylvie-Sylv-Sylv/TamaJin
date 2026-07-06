from database.record import Record


class UserRecord(Record):
    def __init__(self, name: str, display_name: str = None, password_hash: str = None, salt: bytes = None):
        super().__init__(name)

        self.name = name
        self.display_name = display_name
        self._password_hash = password_hash
        self._salt = salt

    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value: str):
        self._password_hash = value

    @property
    def salt(self):
        return self._salt

    @salt.setter
    def salt(self, value: bytes):
        self._salt = value
