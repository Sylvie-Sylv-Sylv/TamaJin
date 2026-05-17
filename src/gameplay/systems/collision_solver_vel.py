from __future__ import annotations
from typing import TYPE_CHECKING

from gameplay.general.vector2d import Vector2D
from gameplay.systems.system import System

if TYPE_CHECKING:
        from gameplay.scenes.physic_scene import PhysicScene


class CollisionSolverVel(System):
        @staticmethod
        def apply_impulse(
                body_a,
                body_b,
                contact_point,
                normal,
                restitution=0.0
        ):
                # lever arms
                ra = contact_point - body_a.position
                rb = contact_point - body_b.position

                # velocity at contact point
                va = body_a.velocity + Vector2D(
                        -body_a.angular_velocity * ra.y,
                        body_a.angular_velocity * ra.x
                )
                vb = body_b.velocity + Vector2D(-body_b.angular_velocity * rb.y, body_b.angular_velocity * rb.x)

                # relative velocity
                rv = vb - va

                # relative velocity along normal
                vel_along_normal = rv.dot(normal)

                # already separating
                if vel_along_normal > 0:
                        return

                # scalar 2D cross products
                ra_cross_n = ra.cross(normal)
                rb_cross_n = rb.cross(normal)

                # effective mass
                inv_mass_sum = (
                        body_a.inverse_mass +
                        body_b.inverse_mass +
                        (ra_cross_n ** 2) * body_a.inverse_inertia +
                        (rb_cross_n ** 2) * body_b.inverse_inertia
                )

                # impulse magnitude
                j = -(1 + restitution) * vel_along_normal
                j /= inv_mass_sum

                impulse = normal * j

                # linear impulse
                body_a.velocity -= impulse * body_a.inverse_mass
                body_b.velocity += impulse * body_b.inverse_mass

                # angular impulse
                body_a.angular_velocity -= (
                        ra.cross(impulse) * body_a.inverse_inertia
                )

                body_b.angular_velocity += (
                        rb.cross(impulse) * body_b.inverse_inertia
                )
        
        @staticmethod
        def step(scene : PhysicScene, dt: float = 1.0):
                pass