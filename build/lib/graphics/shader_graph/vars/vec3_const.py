from graphics.shader_graph.vars.var import Var
from graphics.shader_graph.vars.var_type import VarType

class Vec3Const(Var):
    def __init__(self, x, y, z):
        super().__init__(VarType.VEC3)

        self.x = x
        self.y = y
        self.z = z

    def emit_object(self):
        return f"vec3({self.x}, {self.y}, {self.z})"
    