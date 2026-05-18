from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")

class Scene(ABC):
        @abstractmethod
        def add_entity(self):
                pass
        
        @abstractmethod
        def remove_entity(self):
                pass
        
        @abstractmethod
        def fetch(self, entity_id, component_type: type[T]) -> T | None:
                pass
        
        @abstractmethod
        def query(self):
                pass
        
        @abstractmethod
        def step():
                raise NotImplementedError("Scene step method is not implemented yet.")