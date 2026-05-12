import moderngl as mgl
import pygame as pg
import numpy as np

from texture_array import TextureArray


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

    pg.display.set_mode(
        (800, 600),
        pg.OPENGL | pg.DOUBLEBUF
    )

    ctx = mgl.create_context()

    program = ctx.program(
        vertex_shader=VERTEX_SHADER,
        fragment_shader=FRAGMENT_SHADER
    )

    # Create texture array
    tex_array = TextureArray(
        ctx,
        {
            "test_1": "test_1.png",
            "test_2": "test_2.png"
        },
        mgl.NEAREST
    )

    tex_array.use(0)
    program["texArray"] = 0

    # Two quads side by side
    #
    # Format:
    # x, y, u, v, tex_index

    vertices = np.array([
        # LEFT QUAD (test_1)
        -0.9, -0.5, 0.0, 0.0, tex_array.get_index("test_1"),
        -0.1, -0.5, 1.0, 0.0, tex_array.get_index("test_1"),
        -0.1,  0.5, 1.0, 1.0, tex_array.get_index("test_1"),

        -0.9, -0.5, 0.0, 0.0, tex_array.get_index("test_1"),
        -0.1,  0.5, 1.0, 1.0, tex_array.get_index("test_1"),
        -0.9,  0.5, 0.0, 1.0, tex_array.get_index("test_1"),

        # RIGHT QUAD (test_2)
         0.1, -0.5, 0.0, 0.0, tex_array.get_index("test_2"),
         0.9, -0.5, 1.0, 0.0, tex_array.get_index("test_2"),
         0.9,  0.5, 1.0, 1.0, tex_array.get_index("test_2"),

         0.1, -0.5, 0.0, 0.0, tex_array.get_index("test_2"),
         0.9,  0.5, 1.0, 1.0, tex_array.get_index("test_2"),
         0.1,  0.5, 0.0, 1.0, tex_array.get_index("test_2"),
    ], dtype="f4")

    vbo = ctx.buffer(vertices.tobytes())

    vao = ctx.vertex_array(
        program,
        [
            (
                vbo,
                "2f 2f 1f",
                "in_pos",
                "in_uv",
                "in_tex_index"
            )
        ]
    )

    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        ctx.clear(0.1, 0.1, 0.1)

        vao.render()

        pg.display.flip()
        clock.tick(60)

    vao.release()
    vbo.release()
    tex_array.release()
    program.release()

    pg.quit()


if __name__ == "__main__":
    main()