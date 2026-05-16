from __future__ import annotations

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

        @property
        def left(self):
                return self.x

        @property
        def right(self):
                return self.x + self.width

        @property
        def top(self):
                return self.y

        @property
        def bottom(self):
                return self.y + self.height

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

        def __repr__(self):
                return (
                        f"AABB("
                        f"x={self.x}, "
                        f"y={self.y}, "
                        f"w={self.width}, "
                        f"h={self.height}"
                        f")"
                )