from shader_graph.nodes.node import Node

class Vec4Node(Node):
    def __init__(self, *args):
        super().__init__("vec4", list(args))

    def emit(self):
        args_glsl = ", ".join(arg.glsl() for arg in self.inputs)

        return f"vec4 {self.id} = vec4({args_glsl});"
    