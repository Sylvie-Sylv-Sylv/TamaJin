from __future__ import annotations
from typing import TYPE_CHECKING

from gameplay.general.vector2d import Vec2
from gameplay.systems.system import System
from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position

if TYPE_CHECKING:
        from gameplay.scenes.physic_scene import PhysicScene

class BroadPhaseCollision(System):
        @staticmethod
        def step(scene: PhysicScene):
                scene.broad_collision_pairs.clear()

                for entity, aabb, position in scene.query(AABB, Position):
                        world_aabb = AABB(
                                aabb['x'] + position['x'],
                                aabb['y'] + position['y'],
                                aabb['width'],
                                aabb['height']
                        )
                        
                        possible_collisions = scene.tree.query(world_aabb)

                        for other_entity in possible_collisions:
                                if other_entity == entity:
                                        continue
                                
                                if entity < other_entity:
                                        pair = (entity, other_entity)
                                else:
                                        pair = (other_entity, entity)

                                scene.broad_collision_pairs.add(pair)