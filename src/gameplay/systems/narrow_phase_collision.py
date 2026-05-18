from __future__ import annotations
from typing import TYPE_CHECKING

from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.rotation import Rotation
from gameplay.systems.system import System

if TYPE_CHECKING:
        from gameplay.scenes.physic_scene import PhysicScene


class NarrowPhaseCollision(System):
        @staticmethod
        def step(scene : PhysicScene):
                for entity_a, entity_b in scene.broad_collision_pairs:
                        if (polygon_a := scene.fetch(entity_a, Polygon)) \
                           and (polygon_b := scene.fetch(entity_b, Polygon)):
                                moved_a = polygon_a
                                moved_b = polygon_b
                                
                                if (rotation_a := scene.fetch(entity_a, Rotation)) \
                                   and (rotation_b := scene.fetch(entity_b, Rotation)):
                                        moved_a = moved_a.rotate(rotation_a.val)
                                        moved_b = moved_b.rotate(rotation_b.val)
                                if (position_a := scene.fetch(entity_a, Position)) \
                                   and (position_b := scene.fetch(entity_b, Position)):
                                        moved_a = moved_a.move(position_a)
                                        moved_b = moved_b.move(position_b)

                                        if results := moved_a.sat(moved_b):
                                                is_colliding = results[0]
                                                mtv = results[1]
                                                
                                                if entity_a > entity_b:
                                                        pair = (entity_b, entity_a)
                                                        mtv = -mtv
                                                else:
                                                        pair = (entity_a, entity_b)
                                                
                                                if is_colliding and pair not in scene.narrow_collision_pairs:
                                                        scene.narrow_collision_pairs.add(pair)
                                                        scene.narrow_collision_mtv[pair] = mtv
                                                        
                                                        sep_a = moved_a.move(mtv * 0.5 * 0.999)
                                                        sep_b = moved_b.move(-mtv * 0.5 * 0.999)
                                                        
                                                        scene.narrow_collision_contacts[pair] = sep_a.contact_points(sep_b, mtv)