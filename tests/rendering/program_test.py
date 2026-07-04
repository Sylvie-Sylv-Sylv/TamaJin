import pygame as pg
import moderngl as mgl
import sys

from graphics.vertex import Vertex
from graphics.mesh import Mesh
from graphics.shader_graph import *


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

    # ------------------------
    # Graph Loliconstructor
    # ------------------------

    vertex_builder = ShaderBuilder()

    in_vert = vertex_builder.add_in(VarType.VEC2, "in_vert")
    in_color = vertex_builder.add_in(VarType.VEC3, "in_color")

    v_color = vertex_builder.add_out(VarType.VEC3, "v_color")

    add = AddNode(in_vert, Vec2Const(0.1, 0.1))
    set_color = SetNode(v_color, in_color)
    set_position = SetNode(
        DefinedVar(VarType.VEC4, "gl_Position"),
        VecNode(add, FloatConst(0.0), FloatConst(1.0)),
    )

    vertex_builder.set_ends([set_color, set_position])

    # ------------------------
    # Fragment Loliconstructor
    # ------------------------

    fragment_builder = ShaderBuilder()

    v_color = fragment_builder.add_in(VarType.VEC3, "v_color")
    f_color = fragment_builder.add_out(VarType.VEC4, "f_color")

    add = AddNode(v_color, Vec3Const(0.1, 0.1, 0.1))
    final_color = VecNode(add, FloatConst(1.0))
    set_frag = SetNode(f_color, final_color)

    fragment_builder.set_ends([set_frag])

    # ------------------------
    # Program
    # ------------------------

    program = Program(ctx, vertex_builder, fragment_builder)

    print(program.vertex_shader)
    print(program.fragment_shader)

    vertices = [
        Vertex(program.mgl, in_vert=[0.0, 0.5], in_color=[1.0, 0.0, 0.0]),  # Top Red
        Vertex(
            program.mgl, in_vert=[-0.5, -0.5], in_color=[0.0, 1.0, 0.0]
        ),  # Bottom-Left Green
        Vertex(
            program.mgl, in_vert=[0.5, -0.5], in_color=[0.0, 0.0, 1.0]
        ),  # Bottom-Right Blue
    ]

    mesh = Mesh(ctx, vertices, program.mgl)

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
