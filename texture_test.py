import pygame as pg
import moderngl as mgl

from vertex import Vertex
from mesh import Mesh
from texture import Texture


VERTEX_SHADER = """
#version 330

in vec2 in_position;
in vec2 in_uv;

out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    uv = in_uv;
}
"""

FRAGMENT_SHADER = """
#version 330

uniform sampler2D tex;

in vec2 uv;

out vec4 fragColor;

void main() {
    fragColor = texture(tex, uv);
}
"""


def main():
    # Init pygame + OpenGL context
    pg.init()

    pg.display.set_mode(
        (800, 600),
        pg.OPENGL | pg.DOUBLEBUF
    )

    # Create ModernGL context
    ctx = mgl.create_context()

    # Compile shader program
    program = ctx.program(
        vertex_shader=VERTEX_SHADER,
        fragment_shader=FRAGMENT_SHADER
    )

    # Quad vertices
    #
    #  (-0.5,  0.5) ------ (0.5,  0.5)
    #         |                |
    #         |                |
    #  (-0.5, -0.5) ------ (0.5, -0.5)
    #
    vertices = [
        # Triangle 1
        Vertex(
            program,
            in_position=(-0.5, -0.5),
            in_uv=(0.0, 0.0)
        ),
        Vertex(
            program,
            in_position=(0.5, -0.5),
            in_uv=(1.0, 0.0)
        ),
        Vertex(
            program,
            in_position=(0.5, 0.5),
            in_uv=(1.0, 1.0)
        ),

        # Triangle 2
        Vertex(
            program,
            in_position=(-0.5, -0.5),
            in_uv=(0.0, 0.0)
        ),
        Vertex(
            program,
            in_position=(0.5, 0.5),
            in_uv=(1.0, 1.0)
        ),
        Vertex(
            program,
            in_position=(-0.5, 0.5),
            in_uv=(0.0, 1.0)
        ),
    ]

    # Create mesh
    mesh = Mesh(
        ctx=ctx,
        vertices=vertices,
        program=program
    )

    # Load texture
    texture = Texture(
        ctx,
        "test.png"  # put an image next to this script
    )

    # Bind texture uniform
    program["tex"] = 0

    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # Clear screen
        ctx.clear(0.1, 0.1, 0.1)

        # Use texture
        texture.use(0)

        # Render mesh
        mesh.render()

        # Swap buffers
        pg.display.flip()

        clock.tick(60)

    # Cleanup
    mesh.release()
    texture.release()

    pg.quit()


if __name__ == "__main__":
    main()