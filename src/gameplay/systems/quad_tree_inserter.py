from gameplay.physics.aabb import AABB
from gameplay.scene import Scene
from gameplay.systems.system import System

class QuadTreeInserter(System):
        @staticmethod
        def step(scene : Scene):
                for entity, aabb in scene.query(AABB):
                        scene.tree.insert(entity, aabb)