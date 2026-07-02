import moderngl as mgl
import pygame as pg
import sys

from graphics.texture_array import TextureArray
from graphics.vertex import Vertex
from graphics.mesh import Mesh


VERTEX_SHADER = """
#version 330

in vec2 in_pos;
in vec2 in_uv;
in float in_tex_index;

out vec2 uv;
flat out int tex_index;

void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);

    uv = in_uv;
    tex_index = int(in_tex_index);
}
"""

FRAGMENT_SHADER = """
#version 330

uniform sampler2DArray texArray;

in vec2 uv;
flat in int tex_index;

out vec4 fragColor;

void main() {
    fragColor = texture(texArray, vec3(uv, tex_index));
}
"""


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

    program = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

    # ==========================================================
    # Texture Array
    # ==========================================================

    tex_array = TextureArray(
        ctx,
        {
            "test_1": "resources/test-resources/test_1.png",
            "test_2": "resources/test-resources/test_2.png",
        },
        mgl.NEAREST,
    )

    tex_array.use(0)
    program["texArray"] = 0

    # ==========================================================
    # Vertices
    # ==========================================================

    t1 = tex_array.get_index("test_1")
    t2 = tex_array.get_index("test_2")

    vertices = [
        # ======================================================
        # LEFT QUAD
        # ======================================================
        Vertex(program, in_pos=[-0.9, -0.5], in_uv=[0.0, 0.0], in_tex_index=t1),
        Vertex(program, in_pos=[-0.1, -0.5], in_uv=[1.0, 0.0], in_tex_index=t1),
        Vertex(program, in_pos=[-0.1, 0.5], in_uv=[1.0, 1.0], in_tex_index=t1),
        Vertex(program, in_pos=[-0.9, -0.5], in_uv=[0.0, 0.0], in_tex_index=t1),
        Vertex(program, in_pos=[-0.1, 0.5], in_uv=[1.0, 1.0], in_tex_index=t1),
        Vertex(program, in_pos=[-0.9, 0.5], in_uv=[0.0, 1.0], in_tex_index=t1),
        # ======================================================
        # RIGHT QUAD
        # ======================================================
        Vertex(program, in_pos=[0.1, -0.5], in_uv=[0.0, 0.0], in_tex_index=t2),
        Vertex(program, in_pos=[0.9, -0.5], in_uv=[1.0, 0.0], in_tex_index=t2),
        Vertex(program, in_pos=[0.9, 0.5], in_uv=[1.0, 1.0], in_tex_index=t2),
        Vertex(program, in_pos=[0.1, -0.5], in_uv=[0.0, 0.0], in_tex_index=t2),
        Vertex(program, in_pos=[0.9, 0.5], in_uv=[1.0, 1.0], in_tex_index=t2),
        Vertex(program, in_pos=[0.1, 0.5], in_uv=[0.0, 1.0], in_tex_index=t2),
    ]

    # ==========================================================
    # Mesh
    # ==========================================================

    mesh = Mesh(ctx, vertices, program)

    # ==========================================================
    # Main Loop
    # ==========================================================

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

    # ==========================================================
    # Cleanup
    # ==========================================================

    mesh.release()
    tex_array.release()
    program.release()

    pg.quit()


if __name__ == "__main__":
    main()
