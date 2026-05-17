class Mass:
        def __init__(self, val: float):
                self.val = val
        
        @property
        def inv(self):
                if self.val == 0:
                        raise ValueError("Mass value cannot be zero when calculating inverse.")
                return 1 / self.val