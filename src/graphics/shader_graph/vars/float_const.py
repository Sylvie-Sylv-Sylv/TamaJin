from src.graphics.shader_graph.vars.var import Var
from src.graphics.shader_graph.vars.var_type import VarType

class FloatConst(Var):
    def __init__(self, value):
        super().__init__(VarType.FLOAT)

        self.value = value

    def emit_object(self):
        return str(self.value)
    