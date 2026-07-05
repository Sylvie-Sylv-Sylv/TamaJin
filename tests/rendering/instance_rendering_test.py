import pygame as pg
import moderngl as mgl
import sys

from graphics.mesh import Mesh
from graphics.vertex import Vertex


VERTEX_SHADER = """
#version 330

in vec2 in_pos;
in vec2 in_uv;

in vec2 i_pos;
in float i_tex_index;

out vec2 uv;
flat out int tex_index;

void main() {

    gl_Position = vec4(
        in_pos + i_pos,
        0.0,
        1.0
    );

    uv = in_uv;

    tex_index = int(i_tex_index);
}
"""

FRAGMENT_SHADER = """
#version 330

in vec2 uv;
flat in int tex_index;

out vec4 fragColor;

void main() {

    if (tex_index == 0)
        fragColor = vec4(1.0, 0.0, 0.0, 1.0);

    else if (tex_index == 1)
        fragColor = vec4(0.0, 1.0, 0.0, 1.0);

    else if (tex_index == 2)
        fragColor = vec4(0.0, 0.0, 1.0, 1.0);

    else
        fragColor = vec4(1.0, 1.0, 1.0, 1.0);
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
    # QUAD MESH
    # ==========================================================

    vertices = [
        # Triangle 1
        Vertex(program, in_pos=[-0.08, -0.08], in_uv=[0.0, 0.0]),
        Vertex(program, in_pos=[0.08, -0.08], in_uv=[1.0, 0.0]),
        Vertex(program, in_pos=[0.08, 0.08], in_uv=[1.0, 1.0]),
        # Triangle 2
        Vertex(program, in_pos=[-0.08, -0.08], in_uv=[0.0, 0.0]),
        Vertex(program, in_pos=[0.08, 0.08], in_uv=[1.0, 1.0]),
        Vertex(program, in_pos=[-0.08, 0.08], in_uv=[0.0, 1.0]),
    ]

    mesh = Mesh(ctx, vertices, program)

    # ==========================================================
    # INSTANCE DATA
    # ==========================================================

    instances = []

    grid_size = 5
    spacing = 0.18

    half = (grid_size - 1) / 2

    for y in range(grid_size):

        for x in range(grid_size):

            px = (x - half) * spacing
            py = (y - half) * spacing

            tex_index = (x + y) % 3

            instances.append(
                Vertex(
                    program, is_instance=True, i_pos=[px, py], i_tex_index=[tex_index]
                )
            )

    mesh.set_instances(instances)

    # ==========================================================
    # MAIN LOOP
    # ==========================================================

    clock = pg.time.Clock()

    running = True

    while running:

        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False

        ctx.clear(0.1, 0.1, 0.1)

        mesh.render_instanced()

        pg.display.flip()

        clock.tick(60)

    mesh.release()

    pg.quit()


if __name__ == "__main__":
    main()
