import moderngl as mgl

from i_unit import IUnit

class Mesh(IUnit):
    def __init__(self, ctx: mgl.Context, vertices: list, program: mgl.Program, render_mode = mgl.TRIANGLES):
        """
        :param vertices: A list of Vertex objects that introspected the program.
        """
        self.ctx = ctx
        self.program = program
        self.vertices = vertices
        
        if not vertices:
            raise ValueError("Vertex list cannot be empty.")

        data = b''.join([v.pack() for v in self.vertices])
        
        self.vbo = self.ctx.buffer(data)
        
        sample = self.vertices[0]
        self.format_str = sample.format_str
        self.attributes = sample.attributes
        
        self.vao = self.ctx.vertex_array(
            self.program, 
            [(self.vbo, self.format_str, *self.attributes)]
        )
        
        self.render_mode = render_mode

    def render(self):
        self.vao.render(self.render_mode)

    def release(self):
        self.vbo.release()
        self.vao.release()