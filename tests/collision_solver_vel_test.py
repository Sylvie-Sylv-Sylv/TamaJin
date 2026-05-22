import pygame as pygame
import time
import random

from gameplay.physics.aabb import AABB
from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.mass import Mass
from gameplay.physics.new_force import NewForce
from gameplay.physics.old_force import OldForce
from gameplay.physics.position import Position
from gameplay.physics.polygon import Polygon
from gameplay.physics.rotation import Rotation
from gameplay.physics.velocity import Velocity
from gameplay.scenes.physic_scene import PhysicScene


def _make_square(size: float):
        # local-space square centered at origin
        c = 30
        s = size / 2.0
        return [
                (-s + random.uniform(-c, c), -s + random.uniform(-c, c)),
                (s + random.uniform(-c, c), -s + random.uniform(-c, c)),
                (s + random.uniform(-c, c), s + random.uniform(-c, c)),
                (-s + random.uniform(-c, c), s + random.uniform(-c, c)),
        ]


def main():
        pygame.init()

        window = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()

        scene = PhysicScene()
        scene.initialize()

        # Two overlapping polygons (same size, slightly offset)
        poly_a = Polygon(_make_square(120)).centered()
        poly_b = Polygon(_make_square(120)).centered()

        scene.add_entity(
                "poly_a",
                {
                        Position: (200.0, 200.0),
                        Velocity: (5.0, 0.0),
                        OldForce: (0.0, 0.0),
                        NewForce: (0.002, 0.0),
                        Rotation: (0.0,),
                        AngularVelocity: (0.0,),
                        Mass: (1.0, 1.0),
                        AABB: poly_a.compute_aabb(),
                        Polygon: poly_a,
                }
        )
        scene.add_entity(
                "poly_b",
                {
                        Position: (600.0, 150.0),
                        Velocity: (0.0, 0.0),
                        OldForce: (0.0, 0.0),
                        NewForce: (0.0, 0.0),
                        Rotation: (0.0,),
                        AngularVelocity: (0.1,),
                        Mass: (6.0, 1.0 / 6.0),
                        AABB: poly_b.compute_aabb(),
                        Polygon: poly_b,
                }
        )

        running = True
        while running:
                window.fill((0, 0, 0))
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False
                                
                scene.step(dt = 1, substeps = 4)

                scene.tree.pg_render(window, width=1)

                pos_a = scene.fetch("poly_a", Position)
                pos_b = scene.fetch("poly_b", Position)
                rot_a = scene.fetch("poly_a", Rotation)
                rot_b = scene.fetch("poly_b", Rotation)
                poly_a = scene.fetch("poly_a", Polygon)
                poly_b = scene.fetch("poly_b", Polygon)

                if all(c is not None for c in [pos_a, pos_b, rot_a, rot_b, poly_a, poly_b]):
                        moved_a = poly_a.rotate(rot_a['val']).move(pos_a)
                        moved_b = poly_b.rotate(rot_b['val']).move(pos_b)

                        moved_a.pg_render(window, (255, 255, 255))
                        moved_b.pg_render(window, (255, 255, 255))
                        
                        contact_points = scene.narrow_collision_contacts.get(("poly_a", "poly_b"), [])
                        
                        for point in contact_points:
                                pygame.draw.circle(window, (0, 255, 0), (int(point[0]), int(point[1])), radius = 2)
                                

                pygame.display.flip()
                clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
        main()