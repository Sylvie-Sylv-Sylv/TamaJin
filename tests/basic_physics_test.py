import pygame as pygame
import math

from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.new_force import NewForce
from gameplay.physics.position import Position
from gameplay.physics.rotation import Rotation
from gameplay.physics.velocity import Velocity
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.systems.verlet_first import VerletFirst
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.runtime.quad_tree import QuadTree
from gameplay.physics.aabb import AABB


from gameplay.general.vector2d import Vector2D
from gameplay.physics.aabb import AABB
from gameplay.physics.new_force import NewForce
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.runtime.quad_tree import QuadTree
from gameplay.scenes.sparse_scene import SparseScene
from gameplay.systems.broad_phase_collision import BroadPhaseCollision
from gameplay.systems.collision_solver_pos import CollisionSolverPos
from gameplay.systems.narrow_phase_collision import NarrowPhaseCollision
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.systems.runtime_reset import RuntimeReset
from gameplay.systems.verlet_first import VerletFirst
from gameplay.systems.verlet_second import VerletSecond

class PhysicScene(SparseScene):
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
                self.register_component(Rotation)
                self.register_component(AngularVelocity)
                self.register_component(Mass)
                self.register_component(AABB)
                self.register_component(Polygon)
        
        def step(self, dt: float = 1.0):
                RuntimeReset.step(self)
                VerletFirst.step(self, dt = dt)
                self.tree.clear()
                QuadTreeInserter.step(self)
                BroadPhaseCollision.step(self)
                NarrowPhaseCollision.step(self)
                VerletSecond.step(self, dt = dt)
        

def main():
        pygame.init()

        window = pygame.display.set_mode((800, 600))
        
        scene = PhysicScene()
        
        scene.add_entity("entity_1", Position(100, 100), Velocity(0, 0), OldForce(0, 0), NewForce(0, 0), Mass(1.0), AABB(-32, -32, 64, 64))
        scene.add_entity("entity_2", Position(100, 100), Velocity(0, 0), OldForce(0, 0), NewForce(0, 0), Mass(1.0), AABB(-32, -32, 64, 64))
        
        clock = pygame.time.Clock()
        running = True
        while running:
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False

                scene.step()
                
                if position := scene.fetch("entity_2", Position):
                        position.x  = -math.cos(pygame.time.get_ticks() / 1000.0) * 300 + 100 + 300
                
                window.fill((0, 0, 0))
                
                scene.tree.pg_render(window,  width = 1)
                
                if aabb := scene.fetch("entity_1", AABB):
                        if position := scene.fetch("entity_1", Position):
                                aabb.move(position).pg_render(window, color = (255, 0, 0) if ("entity_1", "entity_2") in scene.broad_collision_pairs else (255, 255, 255))
                
                if aabb := scene.fetch("entity_2", AABB):
                        if position := scene.fetch("entity_2", Position):
                                aabb.move(position).pg_render(window, color = (255, 0, 0) if ("entity_1", "entity_2") in scene.broad_collision_pairs else (255, 255, 255))

                pygame.display.flip()
                clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
        main()