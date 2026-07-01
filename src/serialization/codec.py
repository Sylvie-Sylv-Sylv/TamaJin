from abc import ABC, abstractmethod

from serialization.codecs import Codecs


class Codec(ABC):
    target_type = object
    marker = None

    @abstractmethod
    def encode(self, obj):
        pass

    @abstractmethod
    def decode(self, data):
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Codecs.register(cls)
