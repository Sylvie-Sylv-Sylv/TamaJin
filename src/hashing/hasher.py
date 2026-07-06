from abc import ABC, abstractmethod

class Hasher(ABC):
    """Abstract base class for all password hashing algorithms."""

    @abstractmethod
    def hash(self, string: str, salt: bytes = None) -> str:
        pass

    @abstractmethod
    def verify(self, string: str, hash: str, salt: bytes = None) -> bool:
        pass
    