from graphics.shader_graph.vars.var_type import VarType

class Var:
    def __init__(self, type : VarType):
        self.type = type

    def emit_object(self):
        raise NotImplementedError()
    