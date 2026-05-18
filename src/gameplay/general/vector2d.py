import math

class Vector2D:
        __slots__ = ("x", "y")

        def __init__(self, x: float = 0.0, y: float = 0.0):
                self.x = float(x)
                self.y = float(y)

        # ------------------------
        # Geometry helpers
        # ------------------------

        def perpendicular(self):
                return Vector2D(-self.y, self.x)
        
        # ---
        
        @staticmethod
        def cross_scalar_vec(scalar: float, vec: "Vector2D") -> "Vector2D":
                return Vector2D(-scalar * vec.y, scalar * vec.x)

        # ------------------------
        # Representation
        # ------------------------

        def __str__(self):
                return f"Vector2D({self.x}, {self.y})"

        def __repr__(self):
                return f"Vector2D(x={self.x}, y={self.y})"

        # ------------------------
        # Internal Helpers
        # ------------------------

        @staticmethod
        def _is_scalar(value):
                return isinstance(value, (int, float))

        # ------------------------
        # Arithmetic
        # ------------------------

        def __add__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x + other.x,
                                self.y + other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x + other,
                                self.y + other
                        )

                return NotImplemented

        def __sub__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x - other.x,
                                self.y - other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x - other,
                                self.y - other
                        )

                return NotImplemented

        def __mul__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x * other.x,
                                self.y * other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x * other,
                                self.y * other
                        )

                return NotImplemented

        def __truediv__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x / other.x,
                                self.y / other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x / other,
                                self.y / other
                        )

                return NotImplemented

        def __floordiv__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x // other.x,
                                self.y // other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x // other,
                                self.y // other
                        )

                return NotImplemented

        def __mod__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x % other.x,
                                self.y % other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x % other,
                                self.y % other
                        )

                return NotImplemented

        def __pow__(self, other):
                if isinstance(other, Vector2D):
                        return Vector2D(
                                self.x ** other.x,
                                self.y ** other.y
                        )

                if self._is_scalar(other):
                        return Vector2D(
                                self.x ** other,
                                self.y ** other
                        )

                return NotImplemented

        # ------------------------
        # Reverse Arithmetic
        # ------------------------

        def __radd__(self, other):
                return self.__add__(other)

        def __rsub__(self, other):
                if self._is_scalar(other):
                        return Vector2D(
                                other - self.x,
                                other - self.y
                        )

                return NotImplemented

        def __rmul__(self, other):
                return self.__mul__(other)

        def __rtruediv__(self, other):
                if self._is_scalar(other):
                        return Vector2D(
                                other / self.x,
                                other / self.y
                        )

                return NotImplemented

        # ------------------------
        # In-place Arithmetic
        # ------------------------

        def __iadd__(self, other):
                result = self + other
                self.x, self.y = result.x, result.y
                return self

        def __isub__(self, other):
                result = self - other
                self.x, self.y = result.x, result.y
                return self

        def __imul__(self, other):
                result = self * other
                self.x, self.y = result.x, result.y
                return self

        def __itruediv__(self, other):
                result = self / other
                self.x, self.y = result.x, result.y
                return self

        # ------------------------
        # Unary
        # ------------------------

        def __neg__(self):
                return Vector2D(-self.x, -self.y)

        def __pos__(self):
                return Vector2D(+self.x, +self.y)

        def __abs__(self):
                return Vector2D(abs(self.x), abs(self.y))

        # ------------------------
        # Comparison
        # ------------------------

        def __eq__(self, other):
                return (
                        isinstance(other, Vector2D)
                        and self.x == other.x
                        and self.y == other.y
                )

        # ------------------------
        # Magnitude
        # ------------------------

        @property
        def magnitude(self):
                return math.sqrt(self.x * self.x + self.y * self.y)

        @property
        def magnitude_squared(self):
                return self.x * self.x + self.y * self.y

        # ------------------------
        # Normalization
        # ------------------------

        def normalize(self):
                mag = self.magnitude

                if mag == 0:
                        return Vector2D()

                return self / mag

        def normalize_ip(self):
                mag = self.magnitude

                if mag == 0:
                        return

                self /= mag

        # ------------------------
        # Vector Operations
        # ------------------------

        def dot(self, other):
                return self.x * other.x + self.y * other.y
        
        def cross(self, other):
                return self.x * other.y - self.y * other.x

        def distance_to(self, other):
                return (self - other).magnitude

        def lerp(self, other, t: float):
                return self + (other - self) * t

        def copy(self):
                return Vector2D(self.x, self.y)

        # ------------------------
        # Conversion
        # ------------------------

        def to_tuple(self):
                return (self.x, self.y)

        @classmethod
        def from_tuple(cls, value):
                return cls(*value)
        
        def __hash__(self):
                return hash((self.x, self.y))