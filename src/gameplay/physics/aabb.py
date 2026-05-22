from __future__ import annotations

import numpy as np
import pygame

from gameplay.general.vector2d import Vec2


class AABB:
        """Axis-Aligned Bounding Box used for broad-phase collision detection and spatial partitioning."""
        schema = np.dtype([
                ("x", np.float32),
                ("y", np.float32),
                ("width", np.float32),
                ("height", np.float32)
        ], align=True)

        def __init__(
                self,
                x: float,
                y: float,
                width: float,
                height: float
        ):
                self.x = x
                self.y = y

                self.width = width
                self.height = height

        def to_tuple(self) -> tuple:
                """Convert to tuple for numpy array storage."""
                return (self.x, self.y, self.width, self.height)

        # ------------------------
        # Edge Properties
        # ------------------------

        @property
        def left(self) -> float:
                return self.x

        @property
        def right(self) -> float:
                return self.x + self.width

        @property
        def top(self) -> float:
                return self.y

        @property
        def bottom(self) -> float:
                return self.y + self.height

        # ------------------------
        # Position / Size
        # ------------------------

        @property
        def position(self) -> Vec2:
                return (self.x, self.y)

        @position.setter
        def position(self, value: Vec2):
                self.x = value[0]
                self.y = value[1]

        @property
        def size(self) -> Vec2:
                return (self.width, self.height)

        @size.setter
        def size(self, value: Vec2):
                self.width = value[0]
                self.height = value[1]

        @property
        def center(self) -> Vec2:
                return (
                        self.x + self.width / 2,
                        self.y + self.height / 2
                )

        # ------------------------
        # Geometry
        # ------------------------

        def intersects(self, other: AABB) -> bool:
                """Standard AABB vs AABB intersection check."""
                return not (
                        self.right < other.left
                        or self.left > other.right
                        or self.bottom < other.top
                        or self.top > other.bottom
                )

        def contains(self, other: AABB) -> bool:
                return (
                        other.left >= self.left
                        and other.right <= self.right
                        and other.top >= self.top
                        and other.bottom <= self.bottom
                )

        def contains_point(self, point: Vec2) -> bool:
                return (
                        self.left <= point[0] <= self.right
                        and self.top <= point[1] <= self.bottom
                )

        # ------------------------
        # Transformations
        # ------------------------

        def move(self, offset: Vec2) -> AABB:
                return AABB(
                        self.x + offset[0],
                        self.y + offset[1],
                        self.width,
                        self.height
                )

        def move_ip(self, offset: Vec2):
                self.x += offset[0]
                self.y += offset[1]

        def expanded(self, amount: Vec2) -> AABB:
                return AABB(
                        self.x - amount[0],
                        self.y - amount[1],
                        self.width + amount[0] * 2,
                        self.height + amount[1] * 2
                )
        
        def pg_render(self, surface: pygame.Surface, color = (255, 0, 0), **kwargs):
                pygame.draw.rect(
                        surface,
                        color,
                        (float(self.x), float(self.y), float(self.width), float(self.height)),
                        **kwargs
                )

        # ------------------------
        # Representation
        # ------------------------

        def __repr__(self):
                return (
                f"AABB("
                        f"x={self.x}, "
                        f"y={self.y}, "
                        f"w={self.width}, "
                        f"h={self.height}"
                        f")"
                )