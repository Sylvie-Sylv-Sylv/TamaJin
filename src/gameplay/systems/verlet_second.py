from gameplay.physics.new_force import NewForce
from gameplay.systems.system import System

from gameplay.scenes.scene import Scene

from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass

class VerletSecond(System):       
        @staticmethod
        def step(scene : Scene, dt : float):
                for entity, velocity, old_force, new_force, mass in scene.query(Velocity, OldForce, NewForce, Mass):
                        # compute average acceleration (Trapezoidal rule)
                        ax = 0.5 * (old_force['x'] + new_force['x']) * mass['inv']
                        ay = 0.5 * (old_force['y'] + new_force['y']) * mass['inv']
                        
                        # integrate velocity
                        velocity['x'] += ax * dt
                        velocity['y'] += ay * dt
                        
                        # carry over force for next frame
                        old_force['x'] = new_force['x']
                        old_force['y'] = new_force['y']