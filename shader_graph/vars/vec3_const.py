from shader_graph.vars.var import Var

class Vec3Const(Var):
    def __init__(self, x, y, z):
        super().__init__("vec3")

        self.x = x
        self.y = y
        self.z = z

    def glsl(self):
        return f"vec3({self.x}, {self.y}, {self.z})"
    