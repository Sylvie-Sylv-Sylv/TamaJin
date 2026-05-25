from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

class QuadTreeInserter(System):
        @staticmethod
        def step(scene : Scene):
                for entity, aabb, position in scene.query(AABB, Position):
                        world_aabb = AABB(
                                aabb['x'] + position['x'],
                                aabb['y'] + position['y'],
                                aabb['width'],
                                aabb['height']
                        )
                        scene.tree.insert(entity, world_aabb)