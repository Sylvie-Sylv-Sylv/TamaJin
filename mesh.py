import moderngl as mgl

class Mesh:
    def __init__(self, ctx: mgl.Context, vertices: list, program: mgl.Program):
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

    def render(self, mode=mgl.TRIANGLES):
        self.vao.render(mode)

    def release(self):
        self.vbo.release()
        self.vao.release()