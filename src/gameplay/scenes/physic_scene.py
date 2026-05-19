from gameplay.general.vector2d import Vector2D
from gameplay.physics.aabb import AABB
from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.new_force import NewForce
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.rotation import Rotation
from gameplay.physics.velocity import Velocity
from gameplay.runtime.quad_tree import QuadTree
from gameplay.scenes.scene import Scene
from gameplay.systems.broad_phase_collision import BroadPhaseCollision
from gameplay.systems.collision_solver_pos import CollisionSolverPos
from gameplay.systems.collision_solver_vel import CollisionSolverVel
from gameplay.systems.narrow_phase_collision import NarrowPhaseCollision
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.systems.runtime_reset import RuntimeReset
from gameplay.systems.verlet_first import VerletFirst
from gameplay.systems.verlet_second import VerletSecond

class PhysicScene(Scene):
        def __init__(self):
                super().__init__("basic_scene")
                
                self.tree: QuadTree = QuadTree(AABB(0, 0, 800, 800))
                self.broad_collision_pairs: set[tuple[str, str]] = set()
                self.narrow_collision_pairs: set[tuple[str, str]] = set() # (entity_a, entity_b)
                self.narrow_collision_mtv: dict[tuple[str, str], Vector2D] = {} # (entity_a, entity_b) -> MTV vector
                self.narrow_collision_contacts: dict[tuple[str, str], list[Vector2D]] = {} # (entity_a, entity_b) -> list of contact points
                
                self.register_component('position')
                self.register_component('velocity')
                self.register_component('old_force')
                self.register_component('new_force')
                self.register_component('rotation')
                self.register_component('angular_velocity')
                self.register_component('mass')
                self.register_component('aabb')
                self.register_component('polygon')
        
        def step(self, dt: float = 1.0):
                RuntimeReset.step(self)
                VerletFirst.step(self, dt = dt)
                self.tree.clear()
                QuadTreeInserter.step(self)
                BroadPhaseCollision.step(self)
                NarrowPhaseCollision.step(self)
                CollisionSolverPos.step(self, dt = dt)
                VerletSecond.step(self, dt = dt)
                CollisionSolverVel.step(self, dt = dt)