from src.gameplay.systems.system import System
from src.gameplay.components.vector2d import Vector2D

class VerletFirst(System):
        @staticmethod
        def step(position : Vector2D, velocity : Vector2D, old_acceleration : Vector2D, dt : float):
                position.x += velocity.x * dt + 0.5 * old_acceleration.x * dt * dt
                position.y += velocity.y * dt + 0.5 * old_acceleration.y * dt * dt