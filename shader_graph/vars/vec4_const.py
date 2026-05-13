from shader_graph.vars.var import Var

class Vec4Const(Var):
    def __init__(self, x, y, z, w):
        super().__init__("vec4")

        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def glsl(self):
        return f"vec4({self.x}, {self.y}, {self.z}, {self.w})"
    