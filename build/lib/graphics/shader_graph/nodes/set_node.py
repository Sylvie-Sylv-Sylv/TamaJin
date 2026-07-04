from graphics.shader_graph.nodes.node import Node
from graphics.shader_graph.vars.var_type import VarType

class SetNode(Node):
    def __init__(self, out_var, value):
        super().__init__(VarType.VOID, [value])

        self.out_var = out_var
        self.value = value

    def emit(self):
        return f"{self.out_var.emit_object()} = {self.value.emit_object()};"

    def emit_object(self):
        return ""
    