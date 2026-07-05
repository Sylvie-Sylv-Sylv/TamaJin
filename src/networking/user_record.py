from database.record import Record


class UserRecord(Record):
    def __init__(self, name: str, username: str = None, password: str = None):
        super().__init__(name)

        self.username = username
        self._password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = value
