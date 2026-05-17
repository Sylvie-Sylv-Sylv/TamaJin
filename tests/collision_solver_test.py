import pygame as pygame
import time
import random

from gameplay.general.vector2d import Vector2D
from gameplay.physics.aabb import AABB
from gameplay.physics.mass import Mass
from gameplay.physics.new_force import NewForce
from gameplay.physics.old_force import OldForce
from gameplay.physics.position import Position
from gameplay.physics.polygon import Polygon
from gameplay.physics.velocity import Velocity
from gameplay.scenes.physic_scene import PhysicScene


def _make_square(size: float) -> list[Vector2D]:
        # local-space square centered at origin
        c = 30
        s = size / 2.0
        return [
                Vector2D(-s + random.uniform(-c, c), -s + random.uniform(-c, c)),
                Vector2D(s + random.uniform(-c, c), -s + random.uniform(-c, c)),
                Vector2D(s + random.uniform(-c, c), s + random.uniform(-c, c)),
                Vector2D(-s + random.uniform(-c, c), s + random.uniform(-c, c)),
        ]


def main():
        pygame.init()

        window = pygame.display.set_mode((800, 600))
        clock = pygame.time.Clock()

        scene = PhysicScene()

        # Two overlapping polygons (same size, slightly offset)
        poly_a = Polygon(_make_square(120))
        poly_b = Polygon(_make_square(120))

        # The scene's broad phase uses AABB components, so we give matching AABBs.
        # Note: Polygon vertices are local space; PhysicScene's renderer doesn't transform.
        # Collision SAT uses local vertices too, so we offset via Position and MTV only.
        scene.add_entity(
                "poly_a",
                Position(200, 250),
                Velocity(0, 0),
                OldForce(0, 0),
                NewForce(0, 0),
                Mass(1.0),
                poly_a.compute_aabb(),
                poly_a,
        )
        scene.add_entity(
                "poly_b",
                Position(300, 250),
                Velocity(0, 0),
                OldForce(0, 0),
                NewForce(0, 0),
                Mass(1.0),
                poly_b.compute_aabb(),
                poly_b,
        )
        
        scene.step()

        running = True
        while running:
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False

                window.fill((0, 0, 0))
                scene.tree.pg_render(window, width=1)

                if (position_a := scene.fetch("poly_a", Position)) \
                   and (position_b := scene.fetch("poly_b", Position)) \
                   and (poly_a := scene.fetch("poly_a", Polygon)) \
                   and (poly_b := scene.fetch("poly_b", Polygon)):
                        moved_a = poly_a.move(position_a)
                        moved_b = poly_b.move(position_b)
                           
                        moved_a.pg_render(window, (255, 255, 255))
                        moved_b.pg_render(window, (255, 255, 255))
                        
                        contact_points = scene.narrow_collision_contacts.get(("poly_a", "poly_b"), [])
                        
                        for point in contact_points:
                                pygame.draw.circle(window, (0, 255, 0), point.to_tuple(), radius = 2)
                                

                pygame.display.flip()
                clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
        main()