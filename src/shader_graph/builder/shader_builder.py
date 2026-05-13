from shader_graph.vars.defined_var import DefinedVar
from shader_graph.nodes.node import Node

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

    def build(self, ends = []):
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
        for node in ends:
            self.dfs(node)

        shader += "\n".join(self.lines)
        shader += "\n"

        shader += "}"

        return shader
    