import moderngl as mgl
from src.graphics.shader_graph.builder.shader_builder import ShaderBuilder


class Program():
    def __init__(self, ctx : mgl.Program, vertex_shader_builder, fragment_shader_builder):
        self.vertex_shader = vertex_shader_builder.build()
        self.fragment_shader = fragment_shader_builder.build()

        self.mgl = ctx.program(
            vertex_shader = self.vertex_shader,
            fragment_shader = self.fragment_shader
        )