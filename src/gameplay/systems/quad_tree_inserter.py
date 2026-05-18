from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.scenes.sparse_scene import SparseScene
from gameplay.systems.system import System

class QuadTreeInserter(System):
        @staticmethod
        def step(scene : SparseScene):
                for entity, aabb, position in scene.query(AABB, Position):
                        scene.tree.insert(entity, aabb.move(position))