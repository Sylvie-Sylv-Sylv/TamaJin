from abc import ABC, abstractmethod

from database.record import Record


class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def ensure_connection(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def hard_reset(self):
        pass

    @abstractmethod
    def execute(self, query, params=None):
        pass

    @abstractmethod
    def save(self, obj: Record):
        pass

    @abstractmethod
    def load(self, name: str) -> Record:
        pass

    @abstractmethod
    def delete(self, obj: Record):
        pass
