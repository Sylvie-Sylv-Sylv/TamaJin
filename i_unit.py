from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
        from unit_holder import UnitHolder

class IUnit(ABC):
        @abstractmethod
        def __init__(self, id : str):
                self.unit_holder : UnitHolder = None
                self.id = id
                