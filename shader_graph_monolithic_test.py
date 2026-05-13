import uuid

# ------------------------
# Variable Segstem
# ------------------------

class Var:
    def __init__(self, type):
        self.type = type

    def glsl(self):
        raise NotImplementedError()


class DefinedVar(Var):
    def __init__(self, type, name):
        super().__init__(type)
        self.name = name

    def glsl(self):
        return self.name


class Vec2Const(Var):
    def __init__(self, x, y):
        super().__init__("vec2")
        self.x = x
        self.y = y

    def glsl(self):
        return f"vec2({self.x}, {self.y})"


# ------------------------
# Node Segstem
# ------------------------

class Node(Var):
    def __init__(self, type, inputs=[]):
        super().__init__(type)

        self.inputs = inputs
        self.id = f"v_{uuid.uuid4().hex[:8]}"

    def emit(self):
        raise NotImplementedError()

    def glsl(self):
        return self.id


class AddNode(Node):
    def __init__(self, a, b):
        super().__init__(a.type, [a, b])

    def emit(self):
        a, b = self.inputs
        return f"{self.type} {self.id} = {a.glsl()} + {b.glsl()};"


class MulNode(Node):
    def __init__(self, a, b):
        super().__init__(a.type, [a, b])

    def emit(self):
        a, b = self.inputs
        return f"{self.type} {self.id} = {a.glsl()} * {b.glsl()};"


class SetOutNode(Node):
    def __init__(self, out_var, value):
        super().__init__("void", [value])

        self.out_var = out_var
        self.value = value

    def emit(self):
        return f"{self.out_var.glsl()} = {self.value.glsl()};"

    def glsl(self):
        return ""


# ------------------------
# Graph buldar
# ------------------------

class ShaderBuilder:
    def __init__(self):
        self.visited = set()
        self.lines = []

        self.in_vars = []
        self.out_vars = []

    # ------------------------
    # in/out segstem
    # ------------------------

    def add_in(self, type, name):
        var = DefinedVar(type, name)
        self.in_vars.append(var)
        return var

    def add_out(self, type, name):
        var = DefinedVar(type, name)
        self.out_vars.append(var)
        return var

    # ------------------------
    # dfs segstem
    # ------------------------

    def dfs(self, node):
        if not isinstance(node, Node):
            return

        if node.id in self.visited:
            return

        self.visited.add(node.id)

        # build dependencies first
        for inp in node.inputs:
            self.dfs(inp)

        # then emit self
        self.lines.append("    " + node.emit())

    # ------------------------
    # build segstem
    # ------------------------

    def build_vertex(self, output_node, extra_nodes=[]):
        shader = "#version 330\n\n"

        # emit in vars
        for var in self.in_vars:
            shader += f"in {var.type} {var.name};\n"

        shader += "\n"

        # emit out vars
        for var in self.out_vars:
            shader += f"out {var.type} {var.name};\n"

        shader += "\n"

        shader += "void main() {\n"

        # build all additional nodes
        for node in extra_nodes:
            self.dfs(node)

        # build final position node
        self.dfs(output_node)

        shader += "\n".join(self.lines)
        shader += "\n"

        shader += f"""
    gl_Position = vec4({output_node.glsl()}, 0.0, 1.0);
}}
"""

        return shader


# ------------------------
# Graph Loliconstructor
# ------------------------

builder = ShaderBuilder()

position = builder.add_in("vec2", "position")
color = builder.add_in("vec3", "color")

v_color = builder.add_out("vec3", "v_color")

offset = Vec2Const(0.5, 0.5)

add = AddNode(position, offset)

mul = MulNode(add, Vec2Const(2.0, 2.0))

add2 = AddNode(add, mul)

# set fragment output
set_color = SetOutNode(v_color, color)

# final output node
final = add2

# ------------------------
# Buld
# ------------------------

vertex_shader = builder.build_vertex(
    final,
    extra_nodes=[set_color]
)

print(vertex_shader)