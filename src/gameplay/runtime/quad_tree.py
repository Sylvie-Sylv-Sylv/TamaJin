from gameplay.physics.aabb import AABB
from gameplay.runtime.quad_node import QuadNode

class QuadTree:
    def __init__(self, bounds : AABB):
        self.root = QuadNode(bounds)

    def insert(
        self,
        entity_id: str,
        aabb: AABB
    ):
        self.root.insert(entity_id, aabb)

    def query(
        self,
        area: AABB
    ):
        return self.root.query(area)