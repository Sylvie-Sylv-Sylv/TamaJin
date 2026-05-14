from src.shader_graph.vars.var import Var
from src.shader_graph.vars.var_type import VarType

class Vec4Const(Var):
    def __init__(self, x, y, z, w):
        super().__init__(VarType.VEC4)

        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def emit_object(self):
        return f"{self.type.value}({self.x}, {self.y}, {self.z}, {self.w})"
    