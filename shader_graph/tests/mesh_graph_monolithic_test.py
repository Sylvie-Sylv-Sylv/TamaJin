from shader_graph import *

# ------------------------
# Graph Loliconstructor
# ------------------------

builder = ShaderBuilder()

position = builder.add_in("vec2", "in_vert")
color = builder.add_in("vec3", "in_color")

v_color = builder.add_out("vec3", "v_color")

set_position = SetNode(DefinedVar("vec4", "gl_Position"), Vec4Node(position, FloatConst(0.0), FloatConst(1.0)))

set_color = SetNode(v_color, color)
# ------------------------
# Buld
# ------------------------

vertex_shader = builder.build(
    ends = [set_position, set_color]
)

print(vertex_shader)

# ------------------------
# Fragment Loliconstructor
# ------------------------

fragment_builder = ShaderBuilder()

v_color = fragment_builder.add_in("vec3", "v_color")

f_color = fragment_builder.add_out("vec4", "f_color")

set_frag = SetNode(DefinedVar("vec4", "f_color"), Vec4Node(v_color, FloatConst(1.0)))

# ------------------------
# Buld
# ------------------------

fragment_shader = fragment_builder.build(
    ends=[set_frag]
)

print(fragment_shader)