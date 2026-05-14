from src.graphics.shader_graph.nodes.node import Node
from src.graphics.shader_graph.vars.var_type import VarType

count_to_type = {
        2: VarType.VEC2,
        3: VarType.VEC3,
        4: VarType.VEC4,
}

class VecNode(Node):
    def __init__(self, *args):
        count = 0
        for arg in args:
                if isinstance(arg.type, VarType) and arg.type in (VarType.DOUBLE, VarType.FLOAT, VarType.INT):
                        count += 1
                elif isinstance(arg.type, VarType) and arg.type == VarType.VEC2:
                        count += 2
                elif isinstance(arg.type, VarType) and arg.type == VarType.VEC3:
                        count += 3
                elif isinstance(arg.type, VarType) and arg.type == VarType.VEC4:
                        count += 4
                else:
                        raise ValueError(f"Unsupported type {arg.type} for VecNode")
            
        assert count in count_to_type, "Vec3Node requires 2, 3, or 4 arguments"
        super().__init__(count_to_type[count], list(args))

    def emit(self):
        args_glsl = ", ".join(arg.emit_object() for arg in self.inputs)

        return f"{self.type.value} {self.id} = {self.type.value}({args_glsl});"
    