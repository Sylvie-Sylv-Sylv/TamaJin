from __future__ import annotations
import math

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
        
        @property
        def centroid(self) -> Vector2D:
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
                direction = other.centroid - self.centroid

                # If the push axis points TOWARDS the other object (dot > 0), 
                # we flip it so it pushes AWAY from the other object.
                if direction.dot(smallest_axis) > 0:
                        smallest_axis = -smallest_axis

                mtv = smallest_axis * smallest_overlap

                return True, mtv
        
        def contact_points(self, other: Polygon, mtv: Vector2D):
                normal = mtv.normalize()

                # 1. Ensure the normal always points from 'self' to 'other'
                if (other.centroid - self.centroid).dot(normal) < 0:
                        normal = normal * -1

                def get_best_edge(poly, n):
                        # Find the vertex furthest in the direction of 'n'
                        max_dot = -float("inf")
                        best_idx = 0
                        for i, v in enumerate(poly.vertices):
                                d = v.dot(n)
                                if d > max_dot:
                                        max_dot = d
                                        best_idx = i

                        # Get adjacent vertices
                        v_curr = poly.vertices[best_idx]
                        v_prev = poly.vertices[(best_idx - 1) % len(poly.vertices)]
                        v_next = poly.vertices[(best_idx + 1) % len(poly.vertices)]

                        # Get normalized edge vectors
                        e_left = (v_curr - v_prev).normalize()
                        e_right = (v_next - v_curr).normalize()

                        # The "best" edge is the one most perpendicular to 'n'
                        if abs(e_left.dot(n)) <= abs(e_right.dot(n)):
                                return [v_prev, v_curr], e_left
                        else:
                                return [v_curr, v_next], e_right

                # 2. Get the most aligned edges from both polygons
                edge1, e1_vec = get_best_edge(self, normal)
                edge2, e2_vec = get_best_edge(other, normal * -1)

                # 3. Determine Reference and Incident edges
                # The reference edge is the one most perpendicular to the collision normal
                if abs(e1_vec.dot(normal)) <= abs(e2_vec.dot(normal)):
                        ref_edge = edge1
                        inc_edge = edge2
                        ref_vec = e1_vec
                else:
                        ref_edge = edge2
                        inc_edge = edge1
                        ref_vec = e2_vec
                        # Normal must always point away from the reference body
                        normal = normal * -1 

                def clip(v1, v2, n, offset):
                        clipped = []
                        d1 = v1.dot(n) - offset
                        d2 = v2.dot(n) - offset

                        # Keep points that are on the positive side of the clipping plane
                        if d1 >= 0: clipped.append(v1)
                        if d2 >= 0: clipped.append(v2)

                        # If points are on opposite sides, calculate the intersection point
                        if d1 * d2 < 0:
                                t = d1 / (d1 - d2)
                                clipped.append(v1 + (v2 - v1) * t)
                        
                        return clipped

                ref_v1, ref_v2 = ref_edge
                inc_v1, inc_v2 = inc_edge

                # 4. Clip the Incident edge against the adjacent side planes of the Reference edge
                # Clip against the plane at ref_v1 perpendicular to ref_vec
                o1 = ref_v1.dot(ref_vec)
                clipped = clip(inc_v1, inc_v2, ref_vec, o1)
                if len(clipped) < 2: return clipped

                # Clip against the plane at ref_v2 perpendicular to -ref_vec
                o2 = ref_v2.dot(ref_vec * -1)
                clipped = clip(clipped[0], clipped[1], ref_vec * -1, o2)
                if len(clipped) < 2: return clipped

                # 5. Keep points that penetrate the reference edge plane
                ref_normal = Vector2D(-ref_vec.y, ref_vec.x)
                # Ensure the reference normal points in the same general direction as our collision normal
                if ref_normal.dot(normal) < 0:
                        ref_normal = ref_normal * -1

                ref_plane_offset = ref_v1.dot(ref_normal)

                contacts = []
                for v in clipped:
                        depth = v.dot(ref_normal) - ref_plane_offset
                        # depth <= 0 means it's inside/touching the reference shape. 
                        # The 1e-4 epsilon handles floating-point errors for resting contacts.
                        if depth <= 1e-4: 
                                contacts.append(v)

                if not contacts:
                        # Fallback if floating point errors completely break the manifold
                        contacts = [(self.center + other.center) * 0.5]

                return contacts
        
        def move(self, position: Position):
                moved_vertices = [v + position for v in self.vertices]
                return Polygon(moved_vertices)
        
        def rotate(self, angle_degrees: float):
                angle_radians = math.radians(angle_degrees)
                cos_a = math.cos(angle_radians)
                sin_a = math.sin(angle_radians)

                rotated_vertices = []
                for v in self.vertices:
                        x_new = v.x * cos_a - v.y * sin_a
                        y_new = v.x * sin_a + v.y * cos_a
                        rotated_vertices.append(Vector2D(x_new, y_new))

                return Polygon(rotated_vertices)
        
        def pg_render(self, surface, color):
                points = [v.to_tuple() for v in self.vertices]
                pygame.draw.polygon(surface, color, points, width=1)