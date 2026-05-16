from __future__ import annotations

import pygame

from gameplay.general.vector2d import Vector2D
from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.physics.shape import Shape

class Polygon(Shape):
        def __init__(self, vertices: list[Vector2D]):
                self.vertices = vertices  # local space

        def compute_aabb(self) -> AABB:
                min_x = min(v.x for v in self.vertices)
                min_y = min(v.y for v in self.vertices)

                max_x = max(v.x for v in self.vertices)
                max_y = max(v.y for v in self.vertices)

                return AABB(
                        min_x,
                        min_y,
                        max_x - min_x,
                        max_y - min_y
                )
                
        def _project(self, axis: Vector2D):
                min_p = float("inf")
                max_p = float("-inf")

                for v in self.vertices:
                        p = v.dot(axis)
                        if p < min_p:
                                min_p = p
                        if p > max_p:
                                max_p = p

                return min_p, max_p
        
        # --- NEW HELPER METHOD ---
        def get_centroid(self) -> Vector2D:
                """Calculates the average center of the polygon to ensure accurate push direction."""
                count = len(self.vertices)
                sum_x = sum(v.x for v in self.vertices)
                sum_y = sum(v.y for v in self.vertices)
                return Vector2D(sum_x / count, sum_y / count)
        
        def sat(self, other: Polygon):
                smallest_overlap = float("inf")
                smallest_axis = None

                # test axes from both polygons
                for polygon in (self, other):
                        verts = polygon.vertices
                        count = len(verts)

                        for i in range(count):
                                p1 = verts[i]
                                p2 = verts[(i + 1) % count]

                                edge = p2 - p1
                                axis = edge.perpendicular()

                                # normalize axis safely
                                axis_mag = axis.magnitude
                                if axis_mag == 0:
                                        continue

                                axis = axis / axis_mag

                                min_a, max_a = self._project(axis)
                                min_b, max_b = other._project(axis)

                                # separating axis check
                                if max_a < min_b or max_b < min_a:
                                        return False, None

                                # overlap size
                                overlap = min(max_a, max_b) - max(min_a, min_b)

                                if overlap < smallest_overlap:
                                        smallest_overlap = overlap
                                        smallest_axis = axis

                # safety check
                if smallest_axis is None:
                        return False, None

                # --- FIXED DIRECTION LOGIC ---
                # Get vector pointing from self to other using their actual centers
                direction = other.get_centroid() - self.get_centroid()

                # If the push axis points TOWARDS the other object (dot > 0), 
                # we flip it so it pushes AWAY from the other object.
                if direction.dot(smallest_axis) > 0:
                        smallest_axis = -smallest_axis

                mtv = smallest_axis * smallest_overlap

                return True, mtv
        
        def move(self, position: Position):
                moved_vertices = [v + position for v in self.vertices]
                return Polygon(moved_vertices)
        
        def pg_render(self, surface, color):
                points = [v.to_tuple() for v in self.vertices]
                pygame.draw.polygon(surface, color, points, width=1)