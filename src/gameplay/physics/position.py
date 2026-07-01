import numpy as np


class Position:
    """Physics position component using numpy dtype for buffer alignment."""

    schema = np.dtype([("x", np.float32), ("y", np.float32)], align=True)
