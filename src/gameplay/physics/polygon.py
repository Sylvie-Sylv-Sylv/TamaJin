from __future__ import annotations
import math

import pygame

from gameplay.general.vector2d import (
    Vec2,
    vec_add,
    vec_sub,
    vec_mul,
    vec_div,
    vec_dot,
    vec_cross,
    vec_perpendicular,
    vec_magnitude,
    vec_normalize,
)
from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.physics.shape import Shape


class Polygon(Shape):
    """Represents a convex polygon defined by a list of local-space vertices."""

    def __init__(self, vertices: list[Vec2]):
        self.vertices = vertices  # local space

    @property
    def area(self) -> float:
        """Calculates the area of the polygon using the Shoelace formula."""
        area = 0.0

        for i in range(len(self.vertices)):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % len(self.vertices)]

            area += vec_cross(p1, p2)

        return abs(area) * 0.5

    def centered(self) -> "Polygon":
        centroid = self.centroid

        centered_vertices = [vec_sub(v, centroid) for v in self.vertices]

        return Polygon(centered_vertices)

    def inertia(self, mass: float) -> float:
        """
        Computes the moment of inertia for the polygon.

        :param mass: Total mass of the object.
        :return: The calculated rotational inertia. Returns inf for degenerate polygons.
        """
        numerator = 0.0
        denominator = 0.0

        count = len(self.vertices)

        for i in range(count):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % count]

            cross = vec_cross(p1, p2)

            numerator += cross * (vec_dot(p1, p1) + vec_dot(p1, p2) + vec_dot(p2, p2))

            denominator += cross

        if abs(denominator) < 1e-8:
            return float("inf")

        inertia = (mass / 6.0) * (numerator / denominator)

        return abs(inertia)

    def compute_aabb(self) -> AABB:
        max_radius = 0.0

        for v in self.vertices:
            dist_sq = v[0] * v[0] + v[1] * v[1]

            if dist_sq > max_radius:
                max_radius = dist_sq

        max_radius = math.sqrt(max_radius)

        return AABB(-max_radius, -max_radius, max_radius * 2, max_radius * 2)

    def _project(self, axis: Vec2):
        min_p = float("inf")
        max_p = float("-inf")

        for v in self.vertices:
            p = vec_dot(v, axis)
            if p < min_p:
                min_p = p
            if p > max_p:
                max_p = p

        return min_p, max_p

    @property
    def centroid(self) -> Vec2:
        """Calculates the average center of the polygon to ensure accurate push direction."""
        count = len(self.vertices)
        sum_x = sum(v[0] for v in self.vertices)
        sum_y = sum(v[1] for v in self.vertices)
        return (sum_x / count, sum_y / count)

    def sat(self, other: "Polygon"):
        """
        Performs the Separating Axis Theorem (SAT) collision test.

        :param other: The other polygon to test against.
        :return: A tuple of (bool, Vec2) indicating if a collision occurred
                 and the Minimum Translation Vector (MTV).
        """
        smallest_overlap = float("inf")
        smallest_axis = None

        # test axes from both polygons
        for polygon in (self, other):
            verts = polygon.vertices
            count = len(verts)

            for i in range(count):
                p1 = verts[i]
                p2 = verts[(i + 1) % count]

                edge = vec_sub(p2, p1)
                axis = vec_perpendicular(edge)

                # normalize axis safely
                axis_mag = vec_magnitude(axis)
                if axis_mag == 0:
                    continue

                axis = vec_div(axis, axis_mag)

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
        direction = vec_sub(other.centroid, self.centroid)

        # If the push axis points TOWARDS the other object (dot > 0),
        # we flip it so it pushes AWAY from the other object.
        if vec_dot(direction, smallest_axis) > 0:
            smallest_axis = vec_mul(smallest_axis, -1)

        mtv = vec_mul(smallest_axis, smallest_overlap)

        return True, mtv

    def contact_points(self, other: "Polygon", mtv: Vec2):
        """
        Finds the contact manifold (points of intersection) between two colliding polygons.
        Uses the Sutherland-Hodgman clipping algorithm against a reference edge.

        :param other: The other colliding polygon.
        :param mtv: The Minimum Translation Vector from the SAT test.
        :return: A list of Vec2 contact points.
        """
        normal = vec_normalize(mtv)

        # 1. Ensure the normal always points from 'self' to 'other'
        if vec_dot(vec_sub(other.centroid, self.centroid), normal) < 0:
            normal = vec_mul(normal, -1)

        def get_best_edge(poly, n):
            # Find the vertex furthest in the direction of 'n'
            max_dot = -float("inf")
            best_idx = 0
            for i, v in enumerate(poly.vertices):
                d = vec_dot(v, n)
                if d > max_dot:
                    max_dot = d
                    best_idx = i

            # Get adjacent vertices
            v_curr = poly.vertices[best_idx]
            v_prev = poly.vertices[(best_idx - 1) % len(poly.vertices)]
            v_next = poly.vertices[(best_idx + 1) % len(poly.vertices)]

            # Get normalized edge vectors
            e_left = vec_normalize(vec_sub(v_curr, v_prev))
            e_right = vec_normalize(vec_sub(v_next, v_curr))

            # The "best" edge is the one most perpendicular to 'n'
            if abs(vec_dot(e_left, n)) <= abs(vec_dot(e_right, n)):
                return [v_prev, v_curr], e_left
            else:
                return [v_curr, v_next], e_right

        # 2. Get the most aligned edges from both polygons
        edge1, e1_vec = get_best_edge(self, normal)
        edge2, e2_vec = get_best_edge(other, vec_mul(normal, -1))

        # 3. Determine Reference and Incident edges
        # The reference edge is the one most perpendicular to the collision normal
        if abs(vec_dot(e1_vec, normal)) <= abs(vec_dot(e2_vec, normal)):
            ref_edge = edge1
            inc_edge = edge2
            ref_vec = e1_vec
        else:
            ref_edge = edge2
            inc_edge = edge1
            ref_vec = e2_vec
            # Normal must always point away from the reference body
            normal = vec_mul(normal, -1)

        def clip(v1, v2, n, offset):
            clipped = []
            d1 = vec_dot(v1, n) - offset
            d2 = vec_dot(v2, n) - offset

            # Keep points that are on the positive side of the clipping plane
            if d1 >= 0:
                clipped.append(v1)
            if d2 >= 0:
                clipped.append(v2)

            # If points are on opposite sides, calculate the intersection point
            if d1 * d2 < 0:
                t = d1 / (d1 - d2)
                clipped.append(vec_add(v1, vec_mul(vec_sub(v2, v1), t)))

            return clipped

        ref_v1, ref_v2 = ref_edge
        inc_v1, inc_v2 = inc_edge

        # 4. Clip the Incident edge against the adjacent side planes of the Reference edge
        # Clip against the plane at ref_v1 perpendicular to ref_vec
        o1 = vec_dot(ref_v1, ref_vec)
        clipped = clip(inc_v1, inc_v2, ref_vec, o1)
        if len(clipped) < 2:
            return clipped

        # Clip against the plane at ref_v2 perpendicular to -ref_vec
        o2 = vec_dot(ref_v2, vec_mul(ref_vec, -1))
        clipped = clip(clipped[0], clipped[1], vec_mul(ref_vec, -1), o2)
        if len(clipped) < 2:
            return clipped

        # 5. Keep points that penetrate the reference edge plane
        ref_normal = vec_perpendicular(ref_vec)
        # Ensure the reference normal points in the same general direction as our collision normal
        if vec_dot(ref_normal, normal) < 0:
            ref_normal = vec_mul(ref_normal, -1)

        ref_plane_offset = vec_dot(ref_v1, ref_normal)

        contacts = []
        for v in clipped:
            depth = vec_dot(v, ref_normal) - ref_plane_offset
            # depth <= 0 means it's inside/touching the reference shape.
            # The 1e-4 epsilon handles floating-point errors for resting contacts.
            if depth <= 1e-4:
                contacts.append(v)

        if not contacts:
            # Fallback if floating point errors completely break the manifold
            contacts = [vec_mul(vec_add(self.centroid, other.centroid), 0.5)]

        return contacts

    def move(self, position):
        # Accept either Position (numpy record) or tuple (x, y)
        if hasattr(position, "__getitem__") and isinstance(position[0], (int, float)):
            offset = (position["x"], position["y"])
        else:
            offset = position
        moved_vertices = [vec_add(v, offset) for v in self.vertices]
        return Polygon(moved_vertices)

    def rotate(self, angle_radians: float):
        cos_a = math.cos(angle_radians)
        sin_a = math.sin(angle_radians)

        rotated_vertices = []
        for v in self.vertices:
            x_new = v[0] * cos_a - v[1] * sin_a
            y_new = v[0] * sin_a + v[1] * cos_a
            rotated_vertices.append((x_new, y_new))

        return Polygon(rotated_vertices)

    def pg_render(self, surface, color):
        points = [(int(v[0]), int(v[1])) for v in self.vertices]
        pygame.draw.polygon(surface, color, points, width=1)
