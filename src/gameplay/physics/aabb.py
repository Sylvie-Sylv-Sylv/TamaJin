from __future__ import annotations

import pygame

from gameplay.general.vector2d import Vector2D


class AABB:
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
        def position(self) -> Vector2D:
                return Vector2D(self.x, self.y)

        @position.setter
        def position(self, value: Vector2D):
                self.x = value.x
                self.y = value.y

        @property
        def size(self) -> Vector2D:
                return Vector2D(self.width, self.height)

        @size.setter
        def size(self, value: Vector2D):
                self.width = value.x
                self.height = value.y

        @property
        def center(self) -> Vector2D:
                return Vector2D(
                        self.x + self.width / 2,
                        self.y + self.height / 2
                )

        # ------------------------
        # Geometry
        # ------------------------

        def intersects(self, other: AABB) -> bool:
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

        def contains_point(self, point: Vector2D) -> bool:
                return (
                        self.left <= point.x <= self.right
                        and self.top <= point.y <= self.bottom
                )

        # ------------------------
        # Transformations
        # ------------------------

        def move(self, offset: Vector2D) -> AABB:
                return AABB(
                        self.x + offset.x,
                        self.y + offset.y,
                        self.width,
                        self.height
                )

        def move_ip(self, offset: Vector2D):
                self.x += offset.x
                self.y += offset.y

        def expanded(self, amount: Vector2D) -> AABB:
                return AABB(
                        self.x - amount.x,
                        self.y - amount.y,
                        self.width + amount.x * 2,
                        self.height + amount.y * 2
                )
        
        def pg_render(self, surface: pygame.Surface, color = (255, 0, 0), **kwargs):
                pygame.draw.rect(
                        surface,
                        color,
                        pygame.Rect(self.x, self.y, self.width, self.height),
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