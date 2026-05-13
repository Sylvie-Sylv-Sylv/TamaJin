from src.shader_graph.nodes.node import Node

class DotNode(Node):
    def __init__(self, a, b, result_type = "float"):
        super().__init__(result_type, [a, b])

    def emit(self):
        a, b = self.inputs
        return f"{self.type} {self.id} = dot({a.glsl()}, {b.glsl()});"
    