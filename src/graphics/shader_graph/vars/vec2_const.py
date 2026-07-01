from src.graphics.shader_graph.vars.var import Var
from src.graphics.shader_graph.vars.var_type import VarType


class Vec2Const(Var):
    def __init__(self, x, y):
        super().__init__(VarType.VEC2)
        self.x = x
        self.y = y

    def emit_object(self):
        return f"vec2({self.x}, {self.y})"
