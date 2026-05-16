from __future__ import annotations
from typing import TYPE_CHECKING

from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.systems.system import System

if TYPE_CHECKING:
        from gameplay.scenes.physic_scene import PhysicScene


class NarrowPhaseCollision(System):
        @staticmethod
        def step(scene : PhysicScene):
                for entity_a, entity_b in scene.broad_collision_pairs:
                        if (polygon_a := scene.fetch(entity_a, Polygon)) \
                           and (polygon_b := scene.fetch(entity_b, Polygon)) \
                           and (position_a := scene.fetch(entity_a, Position)) \
                           and (position_b := scene.fetch(entity_b, Position)):
                                if results := polygon_a.move(position_a).sat(polygon_b.move(position_b)):
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