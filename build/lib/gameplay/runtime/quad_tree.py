import pygame

from gameplay.physics.aabb import AABB
from gameplay.runtime.quad_node import QuadNode

class QuadTree:
        def __init__(self, bounds : AABB):
                self.bounds = bounds
                self.root = QuadNode(bounds)

        def clear(self):
                self.root = QuadNode(self.bounds)

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
        
        def pg_render(
                self,
                surface: pygame.Surface,
                width: int = 1
        ):
                self.root.pg_render(
                        surface,
                        width
                )