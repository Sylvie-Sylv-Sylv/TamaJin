import numpy as np

class Mass:
        """
        Physics mass component. 
        Stored as a pair of (value, inverse) to avoid division during solver steps.
        """
        schema = np.dtype([
                ("val", np.float32),
                ("inv", np.float32)
        ], align=True)