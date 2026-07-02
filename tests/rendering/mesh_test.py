import pygame as pg
import moderngl as mgl
import sys
from graphics.vertex import Vertex
from graphics.mesh import Mesh


def main():
    pg.init()

    if sys.platform == "darwin":
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

    pg.display.set_mode((800, 600), pg.OPENGL | pg.DOUBLEBUF)
    ctx = mgl.create_context()

    prog = ctx.program(
        vertex_shader="""
            #version 330
            in vec2 in_vert;
            in vec3 in_color;
            out vec3 v_color;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_color = in_color;
            }
        """,
        fragment_shader="""
            #version 330
            in vec3 v_color;
            out vec4 f_color;
            void main() {
                f_color = vec4(v_color, 1.0);
            }
        """,
    )

    vertices = [
        Vertex(prog, in_vert=[0.0, 0.5], in_color=[1.0, 0.0, 0.0]),  # Top Red
        Vertex(
            prog, in_vert=[-0.5, -0.5], in_color=[0.0, 1.0, 0.0]
        ),  # Bottom-Left Green
        Vertex(
            prog, in_vert=[0.5, -0.5], in_color=[0.0, 0.0, 1.0]
        ),  # Bottom-Right Blue
    ]

    mesh = Mesh(ctx, vertices, prog)

    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        ctx.clear(0.1, 0.1, 0.1)

        mesh.render()

        pg.display.flip()
        clock.tick(60)

    pg.quit()


if __name__ == "__main__":
    main()
