from abc import ABC, abstractmethod

class IUnit(ABC):
        @abstractmethod
        def __init__(self, id : str):
                self.id = id