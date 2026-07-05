from graphics.shader_graph import *

# ------------------------
# Graph Loliconstructor
# ------------------------

builder = ShaderBuilder()

position = builder.add_in(VarType.VEC2, "position")
color = builder.add_in(VarType.VEC3, "color")

v_color = builder.add_out(VarType.VEC3, "v_color")

add = AddNode(position, Vec2Const(0.5, 0.5))
mul = MulNode(add, Vec2Const(2.0, 2.0))
add2 = AddNode(add, mul)

# set fragment output
set_color = SetNode(v_color, color)

set_position = SetNode(
    DefinedVar(VarType.VEC4, "gl_Position"),
    VecNode(add2, FloatConst(0.0), FloatConst(1.0)),
)

# ------------------------
# Buld
# ------------------------

builder.set_ends([set_color, set_position])
vertex_shader = builder.build()

print(vertex_shader)

# ------------------------
# Fragment Loliconstructor
# ------------------------

fragment_builder = ShaderBuilder()

v_color = fragment_builder.add_in(VarType.VEC3, "v_color")

f_color = fragment_builder.add_out(VarType.VEC4, "f_color")

add = AddNode(v_color, Vec3Const(0.1, 0.1, 0.1))

# vec4(v_color, 1.0)
final_color = VecNode(add, FloatConst(1.0))

set_frag = SetNode(f_color, final_color)

# ------------------------
# Buld
# ------------------------

fragment_builder.set_ends([set_frag])
fragment_shader = fragment_builder.build()

print(fragment_shader)
