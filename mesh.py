import moderngl as mgl

from i_unit import IUnit


class Mesh(IUnit):
    def __init__(
        self,
        ctx: mgl.Context,
        vertices: list,
        program: mgl.Program,
        render_mode=mgl.TRIANGLES
    ):
        """
        :param vertices:
            A list of Vertex objects that introspected the program.
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

        self.instance_vbo = None
        self.instance_format_str = None
        self.instance_attributes = None
        self.instance_count = 0

        self.vao_content = [
            (
                self.vbo,
                self.format_str,
                *self.attributes
            )
        ]

        self.vao = self.ctx.vertex_array(
            self.program,
            self.vao_content
        )

        self.render_mode = render_mode

    # ==========================================================
    # Instancing
    # ==========================================================

    def set_instances(self, instances: list):
        """
        :param instances:
            List of Vertex-like objects containing instance data.

        Example:
            Instance(program, instance_pos=[1,2])
        """

        if not instances:
            raise ValueError("Instance list cannot be empty.")

        self.instance_count = len(instances)

        # Release old instance buffer if replacing
        if self.instance_vbo:
            self.instance_vbo.release()

        instance_data = b''.join(
            [instance.pack() for instance in instances]
        )

        self.instance_vbo = self.ctx.buffer(instance_data)

        sample = instances[0]

        self.instance_format_str = sample.format_str + " /i"
        self.instance_attributes = sample.attributes

        # Rebuild VAO with instance buffer
        self.vao.release()

        self.vao_content = [
            (
                self.vbo,
                self.format_str,
                *self.attributes
            ),
            (
                self.instance_vbo,
                self.instance_format_str,
                *self.instance_attributes
            )
        ]

        self.vao = self.ctx.vertex_array(
            self.program,
            self.vao_content
        )

    def render(self):
        self.vao.render(self.render_mode)

    def render_instanced(self):
        if not self.instance_vbo:
            raise RuntimeError("No instance buffer set.")

        self.vao.render(
            self.render_mode,
            instances=self.instance_count
        )

    def release(self):
        self.vbo.release()

        if self.instance_vbo:
            self.instance_vbo.release()

        self.vao.release()