from graphics.shader_graph.vars.var import Var
from graphics.shader_graph.vars.var_type import VarType


class DefinedVar(Var):
    def __init__(self, type: VarType, name):
        super().__init__(type)
        self.name = name

    def emit_object(self):
        return self.name
