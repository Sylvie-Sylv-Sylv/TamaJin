from shader_graph import *

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
set_color = SetNode(v_color, color)

set_position = SetNode(DefinedVar("vec4", "gl_Position"), Vec4Node(add2, FloatConst(0.0), FloatConst(1.0)))

# ------------------------
# Buld
# ------------------------

vertex_shader = builder.build(
    ends = [set_color, set_position]
)

print(vertex_shader)

# ------------------------
# Fragment Loliconstructor
# ------------------------

fragment_builder = ShaderBuilder()

v_color = fragment_builder.add_in("vec3", "v_color")

f_color = fragment_builder.add_out("vec4", "f_color")

add = AddNode(v_color, Vec3Const(0.1, 0.1, 0.1))

# vec4(v_color, 1.0)
final_color = Vec4Node(
    add,
    FloatConst(1.0)
)

set_frag = SetNode(f_color, final_color)

# ------------------------
# Buld
# ------------------------

fragment_shader = fragment_builder.build(
    ends=[set_frag]
)

print(fragment_shader)