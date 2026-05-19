import pygame as pygame
import time
import random

from gameplay.general.vector2d import Vector2D
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
        poly_a = Polygon(_make_square(120)).centered()
        poly_b = Polygon(_make_square(120)).centered()

        # The scene's broad phase uses AABB components, so we give matching AABBs.
        # Note: "polygon" vertices are local space; PhysicScene's renderer doesn't transform.
        # Collision SAT uses local vertices too, so we offset via "position" and MTV only.
        scene.add_entity(
                "poly_a",
                position = Position(200, 200),
                velocity = Velocity(5, 0),
                old_force = OldForce(0, 0),
                new_force = NewForce(0.002, 0),
                rotation = Rotation(0),
                angular_velocity = AngularVelocity(0),
                mass = Mass(1),
                aabb = poly_a.compute_aabb(),
                polygon = poly_a,
        )
        scene.add_entity(
                "poly_b",
                position = Position(600, 150),
                velocity = Velocity(0, 0),
                old_force = OldForce(0, 0),
                new_force = NewForce(0, 0),
                rotation = Rotation(0),
                angular_velocity = AngularVelocity(0.1),
                mass = Mass(2),
                aabb = poly_b.compute_aabb(),
                polygon = poly_b,
        )

        running = True
        while running:
                window.fill((0, 0, 0))
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False
                                
                scene.step(1)

                scene.tree.pg_render(window, width=1)

                if (position_a := scene.fetch("poly_a", "position")) \
                   and (position_b := scene.fetch("poly_b", "position")) \
                   and (rotation_a := scene.fetch("poly_a", "rotation")) \
                   and (rotation_b := scene.fetch("poly_b", "rotation")) \
                   and (poly_a := scene.fetch("poly_a", "polygon")) \
                   and (poly_b := scene.fetch("poly_b", "polygon")):
                        moved_a = poly_a.rotate(rotation_a.val).move(position_a)
                        moved_b = poly_b.rotate(rotation_b.val).move(position_b)

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