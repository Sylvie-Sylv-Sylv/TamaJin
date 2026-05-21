import numpy as np
from gameplay.general.vector2d import Vector2D

class NewForce(Vector2D):
        schema = np.dtype([
                ("x", np.float32),
                ("y", np.float32)
        ], align=True)