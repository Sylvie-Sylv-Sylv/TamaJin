import math
from typing import Tuple, Union

# Type alias for 2D vector as raw tuple
Vec2 = Tuple[float, float]
Scalar = Union[int, float]


# ------------------------
# Static Vector Operations
# ------------------------


def vec_add(a: Vec2, b: Vec2) -> Vec2:
    """Add two vectors."""
    return (a[0] + b[0], a[1] + b[1])


def vec_sub(a: Vec2, b: Vec2) -> Vec2:
    """Subtract two vectors."""
    return (a[0] - b[0], a[1] - b[1])


def vec_mul(a: Vec2, scalar: Scalar) -> Vec2:
    """Multiply vector by scalar."""
    return (a[0] * scalar, a[1] * scalar)


def vec_div(a: Vec2, scalar: Scalar) -> Vec2:
    """Divide vector by scalar."""
    return (a[0] / scalar, a[1] / scalar)


def vec_dot(a: Vec2, b: Vec2) -> float:
    """Dot product of two vectors."""
    return a[0] * b[0] + a[1] * b[1]


def vec_cross(a: Vec2, b: Vec2) -> float:
    """2D cross product (returns scalar z-component)."""
    return a[0] * b[1] - a[1] * b[0]


def vec_cross_scalar(scalar: Scalar, vec: Vec2) -> Vec2:
    """Cross product of scalar with vector (2D analog of 3D cross product)."""
    return (-scalar * vec[1], scalar * vec[0])


def vec_perpendicular(vec: Vec2) -> Vec2:
    """Get perpendicular vector (rotated 90 degrees)."""
    return (-vec[1], vec[0])


def vec_magnitude(vec: Vec2) -> float:
    """Magnitude/length of vector."""
    return math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])


def vec_magnitude_squared(vec: Vec2) -> float:
    """Squared magnitude (avoids sqrt for comparisons)."""
    return vec[0] * vec[0] + vec[1] * vec[1]


def vec_normalize(vec: Vec2) -> Vec2:
    """Normalize vector to unit length."""
    mag = vec_magnitude(vec)
    if mag == 0:
        return (0.0, 0.0)
    return (vec[0] / mag, vec[1] / mag)


def vec_distance(a: Vec2, b: Vec2) -> float:
    """Distance between two vectors."""
    return vec_magnitude(vec_sub(a, b))


def vec_neg(vec: Vec2) -> Vec2:
    """Negate vector."""
    return (-vec[0], -vec[1])


def vec_abs(vec: Vec2) -> Vec2:
    """Absolute value of vector components."""
    return (abs(vec[0]), abs(vec[1]))


def vec_lerp(a: Vec2, b: Vec2, t: float) -> Vec2:
    """Linear interpolation between two vectors."""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def vec_equal(a: Vec2, b: Vec2) -> bool:
    """Check if two vectors are equal."""
    return a[0] == b[0] and a[1] == b[1]


def vec_to_tuple(vec: Vec2) -> Vec2:
    """Identity (already a tuple)."""
    return vec


# ------------------------
# Backward Compatible Class
# ------------------------


class Vector2D:
    """
    Backward-compatible Vector2D class.
    For performance-critical code, use the static functions above instead.
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    # ------------------------
    # Geometry helpers
    # ------------------------

    def perpendicular(self) -> "Vector2D":
        return Vector2D(-self.y, self.x)

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
            return Vector2D(self.x + other.x, self.y + other.y)

        if self._is_scalar(other):
            return Vector2D(self.x + other, self.y + other)

        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x - other.x, self.y - other.y)

        if self._is_scalar(other):
            return Vector2D(self.x - other, self.y - other)

        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x * other.x, self.y * other.y)

        if self._is_scalar(other):
            return Vector2D(self.x * other, self.y * other)

        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x / other.x, self.y / other.y)

        if self._is_scalar(other):
            return Vector2D(self.x / other, self.y / other)

        return NotImplemented

    def __floordiv__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x // other.x, self.y // other.y)

        if self._is_scalar(other):
            return Vector2D(self.x // other, self.y // other)

        return NotImplemented

    def __mod__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x % other.x, self.y % other.y)

        if self._is_scalar(other):
            return Vector2D(self.x % other, self.y % other)

        return NotImplemented

    def __pow__(self, other):
        if isinstance(other, Vector2D):
            return Vector2D(self.x**other.x, self.y**other.y)

        if self._is_scalar(other):
            return Vector2D(self.x**other, self.y**other)

        return NotImplemented

    # ------------------------
    # Reverse Arithmetic
    # ------------------------

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        if self._is_scalar(other):
            return Vector2D(other - self.x, other - self.y)

        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        if self._is_scalar(other):
            return Vector2D(other / self.x, other / self.y)

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
        return isinstance(other, Vector2D) and self.x == other.x and self.y == other.y

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
