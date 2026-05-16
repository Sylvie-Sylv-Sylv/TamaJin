from gameplay.systems.system import System

from gameplay.scenes.scene import Scene

from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass

class VerletFirst(System):       
        @staticmethod
        def step(scene : Scene, dt : float):
                for entity, position, velocity, old_force, mass in scene.query(Position, Velocity, OldForce, Mass):
                        # old acceleration
                        a_old = old_force / mass.value
                        
                        # integrate position
                        position += velocity * dt + 0.5 * a_old * dt * dt