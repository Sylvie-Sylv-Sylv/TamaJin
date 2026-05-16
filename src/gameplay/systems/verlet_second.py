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
                        # old acceleration
                        a_old = old_force / mass.value
                        # compute new acceleration
                        a_new = new_force / mass.value
                        
                        # integrate velocity
                        velocity += 0.5 * (a_old + a_new) * dt
                        
                        new_force.x = old_force.x
                        new_force.y = old_force.y