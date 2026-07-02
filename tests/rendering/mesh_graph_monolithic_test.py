from src.graphics.shader_graph import *

# ------------------------
# Graph Loliconstructor
# ------------------------

builder = ShaderBuilder()

position = builder.add_in(VarType.VEC2, "in_vert")
color = builder.add_in(VarType.VEC3, "in_color")

v_color = builder.add_out(VarType.VEC3, "v_color")

set_position = SetNode(
    DefinedVar(VarType.VEC4, "gl_Position"),
    VecNode(position, FloatConst(0.0), FloatConst(1.0)),
)

set_color = SetNode(v_color, color)
# ------------------------
# Buld
# ------------------------

builder.set_ends([set_position, set_color])
vertex_shader = builder.build()

print(vertex_shader)

# ------------------------
# Fragment Loliconstructor
# ------------------------

fragment_builder = ShaderBuilder()

v_color = fragment_builder.add_in(VarType.VEC3, "v_color")

f_color = fragment_builder.add_out(VarType.VEC4, "f_color")

set_frag = SetNode(
    DefinedVar(VarType.VEC4, "f_color"), VecNode(v_color, FloatConst(1.0))
)

# ------------------------
# Buld
# ------------------------

fragment_builder.set_ends([set_frag])
fragment_shader = fragment_builder.build()

print(fragment_shader)
