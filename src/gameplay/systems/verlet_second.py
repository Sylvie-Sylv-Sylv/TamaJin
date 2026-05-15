from src.gameplay.systems.system import System
from src.gameplay.components.vector2d import Vector2D

class VerletSecond(System):
        @staticmethod
        def step(self, old_acceleration : Vector2D, new_acceleration : Vector2D, dt : float):
                new_acceleration.x = old_acceleration.x
                new_acceleration.y = old_acceleration.y