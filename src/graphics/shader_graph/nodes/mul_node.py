from graphics.shader_graph.nodes.node import Node


class MulNode(Node):
    def __init__(self, a, b):
        super().__init__(a.type, [a, b])

    def emit(self):
        a, b = self.inputs
        return f"{self.type.value} {self.id} = {a.emit_object()} * {b.emit_object()};"
