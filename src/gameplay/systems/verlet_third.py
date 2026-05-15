from src.gameplay.systems.system import System
from src.gameplay.components.vector2d import Vector2D

class VerletThird(System):
        @staticmethod
        def step(velocity : Vector2D, old_acceleration : Vector2D, new_acceleration : Vector2D, dt : float):
                velocity.x += 0.5 * (old_acceleration.x + new_acceleration.x) * dt
                velocity.y += 0.5 * (old_acceleration.y + new_acceleration.y) * dt