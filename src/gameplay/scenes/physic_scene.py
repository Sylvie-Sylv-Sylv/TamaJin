from gameplay.general.vector2d import Vector2D
from gameplay.physics.aabb import AABB
from gameplay.physics.new_force import NewForce
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.runtime.quad_tree import QuadTree
from gameplay.scenes.scene import Scene
from gameplay.systems.broad_phase_collision import BroadPhaseCollision
from gameplay.systems.collision_solver_first import CollisionSolverFirst
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
                
                self.register_component(Position)
                self.register_component(Velocity)
                self.register_component(OldForce)
                self.register_component(NewForce)
                self.register_component(Mass)
                self.register_component(AABB)
                self.register_component(Polygon)
        
        def step(self, dt: float = 1.0):
                VerletFirst.step(self, dt = dt)
                self.tree.clear()
                QuadTreeInserter.step(self)
                BroadPhaseCollision.step(self)
                NarrowPhaseCollision.step(self)
                CollisionSolverFirst.step(self, dt = dt)
                VerletSecond.step(self, dt = dt)
                RuntimeReset.step(self)