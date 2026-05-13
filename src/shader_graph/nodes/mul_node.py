from src.shader_graph.nodes.node import Node

class MulNode(Node):
    def __init__(self, a, b):
        super().__init__(a.type, [a, b])

    def emit(self):
        a, b = self.inputs
        return f"{self.type} {self.id} = {a.glsl()} * {b.glsl()};"
    