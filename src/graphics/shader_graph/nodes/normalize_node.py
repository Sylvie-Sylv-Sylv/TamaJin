from src.graphics.shader_graph.nodes.node import Node


class NormalizeNode(Node):
    def __init__(self, a):
        super().__init__(a.type, [a])

    def emit(self):
        a = self.inputs[0]
        return f"{self.type.value} {self.id} = normalize({a.glsl()});"
