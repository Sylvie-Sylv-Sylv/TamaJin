import pygame as pg

from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.force import Force
from gameplay.physics.mass import Mass
from gameplay.scene import Scene
from gameplay.systems.verlet_integrator import VerletIntegrator
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.runtime.quad_tree import QuadTree
from gameplay.physics.aabb import AABB

class TestScene(Scene):
        def __init__(self):
                super().__init__("test_scene")
                
                self.tree = QuadTree(AABB(0, 0, 800, 800))
                
                self.register_component(Position)
                self.register_component(Velocity)
                self.register_component(Force)
                self.register_component(Mass)
                self.register_component(AABB)
        
        def step(self):
                VerletIntegrator.step(self, dt = 1.0)
                self.tree.clear()
                QuadTreeInserter.step(self)
                

def main():
        pg.init()

        window = pg.display.set_mode((800, 600))
        
        scene = TestScene()
        
        scene.add_entity("entity_1", Position(100, 100), Velocity(5, -5), Force(0, 0.3), Mass(1.0), AABB(-16, -16, 32, 32))
        scene.add_entity("entity_2", Position(100, 500), Velocity(5, 5), Force(0, -0.3), Mass(1.0), AABB(-16, -16, 32, 32))
        
        clock = pg.time.Clock()
        running = True
        while running:
                for event in pg.event.get():
                        if event.type == pg.QUIT:
                                running = False

                scene.step()
                
                window.fill((0, 0, 0))
                
                if aabb := scene.fetch("entity_1", AABB):
                        if position := scene.fetch("entity_1", Position):
                                aabb.move(position).pg_render(window)
                
                if aabb := scene.fetch("entity_2", AABB):
                        if position := scene.fetch("entity_2", Position):
                                aabb.move(position).pg_render(window)
                
                scene.tree.pg_render(window,  width = 1)

                pg.display.flip()
                clock.tick(60)

        pg.quit()

if __name__ == "__main__":
        main()