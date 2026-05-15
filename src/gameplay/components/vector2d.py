from src.gameplay.components.component import Component

class Vector2D(Component):
        def __init__(self, x: float = 0.0, y: float = 0.0):
                self.x = x
                self.y = y

        def __str__(self):
                return f"Vector2D({self.x}, {self.y})"