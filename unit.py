from abc import ABC, abstractmethod

class Unit(ABC):
        @abstractmethod
        def __init__(self, id : str):
                self.id = id