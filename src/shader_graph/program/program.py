import moderngl as mgl
from src.shader_graph.builder.shader_builder import ShaderBuilder


class Program(mgl.Program):
    def __init__(self, vertex_shader_builder, fragment_shader_builder):
        vertex_shader = vertex_shader_builder.build()
        fragment_shader = fragment_shader_builder.build()

        super().__init__(
            vertex_shader = vertex_shader,
            fragment_shader = fragment_shader
        )