from gameplay.physics.aabb import AABB
from gameplay.physics.force import Force
from gameplay.physics.mass import Mass
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.runtime.quad_tree import QuadTree
from gameplay.scenes.scene import Scene
from gameplay.systems.broad_phase_collision import BroadPhaseCollision
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.systems.verlet_integrator import VerletIntegrator

class PhysicScene(Scene):
        def __init__(self):
                super().__init__("basic_scene")
                
                self.tree: QuadTree = QuadTree(AABB(0, 0, 800, 800))
                self.broad_collision_pairs: set[tuple[str, str]] = set()
                self.narrow_collision_pairs: set[tuple[str, str]] = set()
                
                self.register_component(Position)
                self.register_component(Velocity)
                self.register_component(Force)
                self.register_component(Mass)
                self.register_component(AABB)
        
        def step(self):
                VerletIntegrator.step(self, dt = 1.0)
                self.tree.clear()
                QuadTreeInserter.step(self)
                BroadPhaseCollision.step(self)