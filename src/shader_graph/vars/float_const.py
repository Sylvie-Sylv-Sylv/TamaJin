from shader_graph.vars.var import Var

class FloatConst(Var):
    def __init__(self, value):
        super().__init__("float")

        self.value = value

    def glsl(self):
        return str(self.value)
    