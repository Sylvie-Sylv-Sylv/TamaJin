from src.shader_graph.nodes.node import Node

class SetNode(Node):
    def __init__(self, out_var, value):
        super().__init__("void", [value])

        self.out_var = out_var
        self.value = value

    def emit(self):
        return f"{self.out_var.glsl()} = {self.value.glsl()};"

    def glsl(self):
        return ""
    