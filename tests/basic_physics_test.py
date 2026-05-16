import pygame as pygame
import math

from gameplay.physics.new_force import NewForce
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.scenes.physic_scene import PhysicScene
from gameplay.systems.verlet_first import VerletFirst
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.runtime.quad_tree import QuadTree
from gameplay.physics.aabb import AABB
        

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