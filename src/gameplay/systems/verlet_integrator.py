from gameplay.systems.system import System

from gameplay.scenes.scene import Scene

from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.force import Force
from gameplay.physics.mass import Mass

class VerletIntegrator(System):
        @staticmethod
        def step(scene : Scene, dt : float):
                for entity, position, velocity, force, mass in scene.query(Position, Velocity, Force, Mass):
                        # old acceleration
                        a_old = force / mass.value
                        
                        # integrate position
                        position += velocity * dt + 0.5 * a_old * dt * dt
                        
                        # compute new acceleration
                        a_new = force / mass.value
                        
                        # integrate velocity
                        velocity += 0.5 * (a_old + a_new) * dt