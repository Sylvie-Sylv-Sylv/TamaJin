from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from gameplay.general.vector2d import Vector2D
from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.mass import Mass
from gameplay.physics.polygon import Polygon
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.systems.system import System

if TYPE_CHECKING:
        from gameplay.scenes.physic_scene import PhysicScene


class CollisionSolverVel(System):
        @staticmethod
        def apply_impulse(
                poly_a: Polygon, poly_b: Polygon,
                pos_a: Position, pos_b: Position,
                velo_a: Velocity, velo_b: Velocity,
                ang_velo_a: AngularVelocity, ang_velo_b: AngularVelocity,
                mass_a: Mass, mass_b: Mass,
                contact: Vector2D, contact_count: int, mtv: Vector2D,
                restitution: float = 0.2
        ):
                # OLD ENGINE CONVENTION:
                # normal points from other -> self
                normal = (mtv).normalize()

                # vectors from centers to contact
                ra = contact - pos_a
                rb = contact - pos_b

                # OLD ENGINE rotational tangential velocity convention
                angular_linear_a = Vector2D(ra.y, ra.x) * ang_velo_a.val
                angular_linear_b = Vector2D(rb.y, rb.x) * ang_velo_b.val

                # velocity at contact
                vel_a = velo_a + angular_linear_a
                vel_b = velo_b + angular_linear_b

                # OLD ENGINE relative velocity convention
                relative_velocity = vel_a - vel_b

                vel_along_normal = relative_velocity.dot(normal)

                # separating
                if vel_along_normal > 0:
                        return

                # OLD ENGINE inertia approximation
                inertia_a = 0.5 * mass_a.val * ra.dot(ra)
                inertia_b = 0.5 * mass_b.val * rb.dot(rb)

                inv_inertia_a = 0.0 if inertia_a == 0 else 1.0 / inertia_a
                inv_inertia_b = 0.0 if inertia_b == 0 else 1.0 / inertia_b

                ra_cross_n = ra.cross(normal)
                rb_cross_n = rb.cross(normal)

                denom = (
                        mass_a.inv +
                        mass_b.inv +
                        (ra_cross_n ** 2) * inv_inertia_a +
                        (rb_cross_n ** 2) * inv_inertia_b
                )

                if denom == 0:
                        return

                j = -(1 + restitution) * vel_along_normal
                j /= denom
                j /= contact_count

                impulse = normal * j

                # OLD ENGINE linear impulse convention
                velo_a.x += impulse.x * mass_a.inv
                velo_a.y += impulse.y * mass_a.inv

                velo_b.x -= impulse.x * mass_b.inv
                velo_b.y -= impulse.y * mass_b.inv

                # OLD ENGINE angular impulse convention
                ang_velo_a.val += ra.cross(impulse) * inv_inertia_a
                ang_velo_b.val -= rb.cross(impulse) * inv_inertia_b
                
        @staticmethod
        def step(scene : PhysicScene, dt: float = 1.0):
                for (entity_a, entity_b) in scene.narrow_collision_pairs:
                        if not (pos_a := scene.fetch(entity_a, Position)) \
                           or not (pos_b := scene.fetch(entity_b, Position)) \
                           or not (velo_a := scene.fetch(entity_a, Velocity)) \
                           or not (velo_b := scene.fetch(entity_b, Velocity)) \
                           or not (ang_velo_a := scene.fetch(entity_a, AngularVelocity)) \
                           or not (ang_velo_b := scene.fetch(entity_b, AngularVelocity)) \
                           or not (mass_a := scene.fetch(entity_a, Mass)) \
                           or not (mass_b := scene.fetch(entity_b, Mass)):
                                print("Warning: Missing components for collision solver velocity. Skipping impulse application.")
                                continue
                        
                        mtv = scene.narrow_collision_mtv[(entity_a, entity_b)]
                        contacts = scene.narrow_collision_contacts[(entity_a, entity_b)]
                        
                        pos_a = scene.fetch(entity_a, Position)
                        pos_b = scene.fetch(entity_b, Position)
                        
                        velo_a = scene.fetch(entity_a, Velocity)
                        velo_b = scene.fetch(entity_b, Velocity)
                        
                        ang_velo_a = scene.fetch(entity_a, AngularVelocity)
                        ang_velo_b = scene.fetch(entity_b, AngularVelocity)
                        
                        mass_a = scene.fetch(entity_a, Mass)
                        mass_b = scene.fetch(entity_b, Mass)
                        
                        poly_a = scene.fetch(entity_a, Polygon)
                        poly_b = scene.fetch(entity_b, Polygon)
                        
                        for contact in contacts[0:1]: # only apply impulse on the first contact point for now
                                CollisionSolverVel.apply_impulse(
                                        poly_a, poly_b,
                                        pos_a, pos_b,
                                        velo_a, velo_b,
                                        ang_velo_a, ang_velo_b,
                                        mass_a, mass_b,
                                        contact, len(contacts), mtv,
                                        1.0
                                )