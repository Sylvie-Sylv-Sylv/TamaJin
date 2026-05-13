from src.shader_graph.vars.var import Var

class DefinedVar(Var):
    def __init__(self, type, name):
        super().__init__(type)
        self.name = name

    def glsl(self):
        return self.name
    