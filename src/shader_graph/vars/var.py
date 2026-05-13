# ------------------------
# Variable Segstem
# ------------------------

class Var:
    def __init__(self, type):
        self.type = type

    def glsl(self):
        raise NotImplementedError()
    