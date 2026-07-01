from abc import ABC, abstractmethod

from typings import TYPE_CHECKING

if TYPE_CHECKING:
    from serialization.codecs import Codecs

class Codec(ABC):
    target_type = object
    
    @abstractmethod
    def encode(self, obj):
        pass

    @abstractmethod
    def decode(self, data):
        pass
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        Codecs.register(cls)