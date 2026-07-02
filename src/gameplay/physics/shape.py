from __future__ import annotations
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def sat(self, other: Shape) -> bool:
        raise NotImplementedError("SAT not implemented for this shape type")
