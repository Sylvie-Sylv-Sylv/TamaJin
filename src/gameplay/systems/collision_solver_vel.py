from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

from gameplay.general.vector2d import Vector2D
from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.mass import Mass
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.rotation import Rotation
from gameplay.systems.system import System

if TYPE_CHECKING:
        from gameplay.scenes.physic_scene import PhysicScene


class CollisionSolverVel(System):
        @staticmethod
        def apply_impulse(
                poly_a: Polygon, poly_b: Polygon,
                pos_a: np.void, pos_b: np.void,
                velo_a: np.void, velo_b: np.void,
                ang_velo_a: np.void, ang_velo_b: np.void,
                mass_a: np.void, mass_b: np.void, dt: float,
                contact: Vector2D, contact_count: int, mtv: Vector2D,
                restitution: float = 0.2
        ):
                # OLD ENGINE CONVENTION:
                # normal points from other -> self
                normal = (mtv).normalize()

                # vectors from centers to contact
                ra = contact - Vector2D(pos_a['x'], pos_a['y'])
                rb = contact - Vector2D(pos_b['x'], pos_b['y'])

                # Correct 2D cross product for tangential velocity: v = ω x r
                angular_linear_a = Vector2D.cross_scalar_vec(ang_velo_a['val'], ra)
                angular_linear_b = Vector2D.cross_scalar_vec(ang_velo_b['val'], rb)

                # velocity at contact
                vel_a = Vector2D(velo_a['x'], velo_a['y']) + angular_linear_a
                vel_b = Vector2D(velo_b['x'], velo_b['y']) + angular_linear_b

                relative_velocity = vel_a - vel_b
                
                vel_along_normal = relative_velocity.dot(normal)

                # Do not apply impulse if bodies are separating or already separated along the normal.
                if vel_along_normal >= 0.0:
                        return

                # Use the actual moment of inertia from the Polygon shape
                inertia_a = poly_a.inertia(mass_a['val'])
                inertia_b = poly_b.inertia(mass_b['val'])

                inv_inertia_a = 0.0 if inertia_a == 0 else 1.0 / inertia_a
                inv_inertia_b = 0.0 if inertia_b == 0 else 1.0 / inertia_b

                ra_cross_n = ra.cross(normal)
                rb_cross_n = rb.cross(normal)

                denom = (
                        mass_a['inv'] +
                        mass_b['inv'] +
                        (ra_cross_n ** 2) * inv_inertia_a +
                        (rb_cross_n ** 2) * inv_inertia_b
                )

                if denom == 0:
                        return

                # --- BAUMGARTE STABILIZATION ---
                # bias_factor: How much of the position error to fix per frame (0.1 to 0.3)
                # slop: Amount of allowed penetration to prevent jitter (0.01 to 0.1)
                bias_factor = 0.2
                slop = 0.05
                penetration_depth = mtv.magnitude
                bias = (bias_factor / dt) * max(0.0, penetration_depth - slop)

                j = -( (1 + restitution) * vel_along_normal + bias )
                j /= denom
                j /= contact_count

                impulse = normal * j

                # OLD ENGINE linear impulse convention
                velo_a['x'] += impulse.x * mass_a['inv']
                velo_a['y'] += impulse.y * mass_a['inv']

                velo_b['x'] -= impulse.x * mass_b['inv']
                velo_b['y'] -= impulse.y * mass_b['inv']

                # OLD ENGINE angular impulse convention
                ang_velo_a['val'] += ra.cross(impulse) * inv_inertia_a
                ang_velo_b['val'] -= rb.cross(impulse) * inv_inertia_b
                
        @staticmethod
        def step(scene : PhysicScene, dt: float = 1.0):
                for (entity_a, entity_b) in scene.narrow_collision_pairs:
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

                        components = [pos_a, pos_b, velo_a, velo_b, ang_velo_a, ang_velo_b, mass_a, mass_b, poly_a, poly_b]
                        if any(c is None for c in components):
                                print("Warning: Missing components for collision solver velocity. Skipping impulse application.")
                                continue
                        
                        mtv = scene.narrow_collision_mtv[(entity_a, entity_b)]
                        contacts = scene.narrow_collision_contacts[(entity_a, entity_b)]
                        
                        for contact in contacts: # only apply impulse on the first contact point for now
                                CollisionSolverVel.apply_impulse(
                                        poly_a, poly_b,
                                        pos_a, pos_b,
                                        velo_a, velo_b,
                                        ang_velo_a, ang_velo_b,
                                        mass_a, mass_b, dt,
                                        contact, len(contacts), mtv,
                                        1.0
                                )