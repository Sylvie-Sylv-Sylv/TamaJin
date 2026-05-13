from src.shader_graph.vars.var import Var

class Vec2Const(Var):
    def __init__(self, x, y):
        super().__init__("vec2")
        self.x = x
        self.y = y

    def glsl(self):
        return f"vec2({self.x}, {self.y})"
    