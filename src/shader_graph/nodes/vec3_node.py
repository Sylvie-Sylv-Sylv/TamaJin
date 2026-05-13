from shader_graph.nodes.node import Node

class Vec3Node(Node):
    def __init__(self, *args):
        super().__init__("vec3", list(args))

    def emit(self):
        args_glsl = ", ".join(arg.glsl() for arg in self.inputs)

        return f"vec3 {self.id} = vec3({args_glsl});"
    