from __future__ import annotations
from typing import TYPE_CHECKING

from gameplay.general.vector2d import Vec2
from gameplay.systems.system import System
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.rotation import Rotation

if TYPE_CHECKING:
    from gameplay.scenes.physic_scene import PhysicScene


class NarrowPhaseCollision(System):
    """
    Performs detailed geometric collision tests on pairs identified by the BroadPhase.
    It populates the collision manifold (MTV and Contact Points) required for
    physical resolution.
    """

    @staticmethod
    def step(scene: PhysicScene):
        for entity_a, entity_b in scene.broad_collision_pairs:
            if (polygon_a := scene.fetch_component(entity_a, Polygon)) is not None and (
                polygon_b := scene.fetch_component(entity_b, Polygon)
            ) is not None:
                moved_a = polygon_a
                moved_b = polygon_b

                if (
                    rotation_a := scene.fetch_component(entity_a, Rotation)
                ) is not None and (
                    rotation_b := scene.fetch_component(entity_b, Rotation)
                ) is not None:
                    moved_a = moved_a.rotate(rotation_a["val"])
                    moved_b = moved_b.rotate(rotation_b["val"])
                if (
                    position_a := scene.fetch_component(entity_a, Position)
                ) is not None and (
                    position_b := scene.fetch_component(entity_b, Position)
                ) is not None:
                    moved_a = moved_a.move((position_a["x"], position_a["y"]))
                    moved_b = moved_b.move((position_b["x"], position_b["y"]))

                    if results := moved_a.sat(moved_b):
                        is_colliding = results[0]
                        mtv = results[1]

                        if entity_a > entity_b:
                            pair = (entity_b, entity_a)
                            mtv = (-mtv[0], -mtv[1])
                        else:
                            pair = (entity_a, entity_b)

                        if is_colliding and pair not in scene.narrow_collision_pairs:
                            scene.narrow_collision_pairs.add(pair)
                            scene.narrow_collision_mtv[pair] = mtv

                            sep_a = moved_a.move(
                                (mtv[0] * 0.5 * 0.999, mtv[1] * 0.5 * 0.999)
                            )
                            sep_b = moved_b.move(
                                (-mtv[0] * 0.5 * 0.999, -mtv[1] * 0.5 * 0.999)
                            )

                            scene.narrow_collision_contacts[pair] = (
                                sep_a.contact_points(sep_b, mtv)
                            )
