from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System

class QuadTreeInserter(System):
        @staticmethod
        def step(scene : Scene):
                for entity, aabb, position in scene.query("aabb", "position"):
                        scene.tree.insert(entity, aabb.move(position))