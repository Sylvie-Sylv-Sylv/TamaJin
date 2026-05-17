import pygame as pygame
import math

from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.new_force import NewForce
from gameplay.physics.position import Position
from gameplay.physics.rotation import Rotation
from gameplay.physics.velocity import Velocity
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.scenes.physic_scene import PhysicScene
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
from gameplay.scenes.scene import Scene
from gameplay.systems.broad_phase_collision import BroadPhaseCollision
from gameplay.systems.collision_solver_pos import CollisionSolverPos
from gameplay.systems.narrow_phase_collision import NarrowPhaseCollision
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.systems.runtime_reset import RuntimeReset
from gameplay.systems.verlet_first import VerletFirst
from gameplay.systems.verlet_second import VerletSecond
        

def main():
        pygame.init()

        window = pygame.display.set_mode((800, 600))
        
        scene = PhysicScene()
        
        polygon = Polygon([
                Vector2D(-32, -32),
                Vector2D(32, -32),
                Vector2D(32, 32),
                Vector2D(-32, 32)
        ])
        
        scene.add_entity(
                "entity_1",
                Position(100, 100), Velocity(0, 0), OldForce(0, 0), NewForce(0, 0),
                Rotation(0), AngularVelocity(1),
                polygon,
                polygon.compute_aabb()
        )
        
        clock = pygame.time.Clock()
        running = True
        while running:
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False

                scene.step()
                
                window.fill((0, 0, 0))
                
                scene.tree.pg_render(window,  width = 1)
                
                if (polygon := scene.fetch("entity_1", Polygon)) \
                   and (position := scene.fetch("entity_1", Position)) \
                   and (rotation := scene.fetch("entity_1", Rotation)):
                        polygon.rotate(rotation.val).move(position).pg_render(window, color = (255, 0, 0) if ("entity_1", "entity_2") in scene.broad_collision_pairs else (255, 255, 255))

                pygame.display.flip()
                clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
        main()