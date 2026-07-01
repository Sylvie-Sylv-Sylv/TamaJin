"""
Pong with ModernGL - Step by step implementation.
"""

import sys
import numpy as np
import pygame
import moderngl as mgl

from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System
from context.context import Context
from gameplay.config.config import Config
from graphics.vertex import Vertex
from graphics.mesh import Mesh


# ============================================================
# COMPONENTS
# ============================================================

class Score:
    schema = np.dtype([
        ("left", np.int32),
        ("right", np.int32),
    ], align=True)


# ============================================================
# SYSTEMS
# ============================================================

class InputSystem(System):
    def __init__(self):
        self.keys = set()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys.discard(event.key)

    def step(self, scene, speed=400, **kwargs):
        controls = {
            "left_paddle": (pygame.K_w, pygame.K_s),
            "right_paddle": (pygame.K_UP, pygame.K_DOWN),
        }

        for entity, (up, down) in controls.items():
            vel = scene.fetch_component(entity, Velocity)
            if vel is None:
                continue

            vel["x"] = 0
            vel["y"] = (
                (speed if up in self.keys else 0) +
                (-speed if down in self.keys else 0)
            )


class MovementSystem(System):
    def step(self, scene, dt=0.0, **kwargs):
        for _, pos, vel in scene.query(Position, Velocity):
            pos["x"] += vel["x"] * dt
            pos["y"] += vel["y"] * dt


class PaddleBoundsSystem(System):
    def step(self, scene, height=600, **kwargs):
        for entity in ("left_paddle", "right_paddle"):
            pos = scene.fetch_component(entity, Position)
            if pos is None:
                continue
            pos["y"] = np.clip(pos["y"], 50, height - 50)


class BallPhysicsSystem(System):
    def step(self, scene: Scene, width=800, height=600, **kwargs):
        ball_pos = scene.fetch_component("ball", Position)
        ball_vel = scene.fetch_component("ball", Velocity)
        score = scene.fetch_component("score", Score)

        if ball_pos is None or ball_vel is None:
            return

        bx = ball_pos["x"]
        by = ball_pos["y"]

        # Wall collision
        if by <= 10:
            ball_pos["y"] = 10
            ball_vel["y"] = abs(ball_vel["y"])
        elif by >= height - 10:
            ball_pos["y"] = height - 10
            ball_vel["y"] = -abs(ball_vel["y"])

        # Paddle collision
        for paddle in ("left_paddle", "right_paddle"):
            pos = scene.fetch_component(paddle, Position)
            if pos is None:
                continue

            px = pos["x"]
            py = pos["y"]

            overlap_x = abs(bx - px) <= 20
            overlap_y = abs(by - py) <= 60

            if overlap_x and overlap_y:
                direction = 1 if paddle == "left_paddle" else -1
                ball_vel["x"] = direction * abs(ball_vel["x"]) * 1.02
                offset = (by - py) / 50
                ball_vel["y"] = offset * 250
                ball_pos["x"] = px + direction * 21

        # Scoring & Reset
        if bx < 0 or bx > width:
            direction = 1 if bx < 0 else -1
            score_key = "right" if bx < 0 else "left"

            if score is not None:
                score[score_key] += 1

            self.reset_ball(ball_pos, ball_vel, width, height, direction)

    @staticmethod
    def reset_ball(pos, vel, width, height, direction):
        pos["x"] = width / 2
        pos["y"] = height / 2
        vel["x"] = direction * 300
        vel["y"] = (np.random.random() - 0.5) * 200


# ============================================================
# RENDER SYSTEM - Step 2: Render ball and paddles
# ============================================================

class GLRenderSystem(System):
    def __init__(self, ctx: mgl.Context, prog: mgl.Program, width: int, height: int):
        self.ctx = ctx
        self.prog = prog
        self.width = width
        self.height = height

        # Create meshes
        self.paddle_mesh = self._create_paddle_mesh(ctx, prog)
        self.ball_mesh = self._create_ball_mesh(ctx, prog)
        self.line_mesh = self._create_line_mesh(ctx, prog)

    def _create_paddle_mesh(self, ctx, prog):
        """Paddle as a quad."""
        # Quad as 2 triangles
        vertices = [
            # Triangle 1
            Vertex(prog, in_pos=[-0.02, -0.1], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[-0.02,  0.1], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[ 0.02, -0.1], in_color=[1.0, 1.0, 1.0]),
            # Triangle 2
            Vertex(prog, in_pos=[-0.02,  0.1], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[ 0.02,  0.1], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[ 0.02, -0.1], in_color=[1.0, 1.0, 1.0]),
        ]
        return Mesh(ctx, vertices, prog, mgl.TRIANGLES)

    def _create_ball_mesh(self, ctx, prog):
        """Ball as a small quad."""
        vertices = [
            Vertex(prog, in_pos=[-0.015, -0.015], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[-0.015,  0.015], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[ 0.015, -0.015], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[-0.015,  0.015], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[ 0.015,  0.015], in_color=[1.0, 1.0, 1.0]),
            Vertex(prog, in_pos=[ 0.015, -0.015], in_color=[1.0, 1.0, 1.0]),
        ]
        return Mesh(ctx, vertices, prog, mgl.TRIANGLES)

    def _create_line_mesh(self, ctx, prog):
        """Center dashed line."""
        vertices = []
        for y in np.arange(-1.0, 1.0, 0.1):
            vertices.append(Vertex(prog, in_pos=[0.0, y], in_color=[0.5, 0.5, 0.5]))
            vertices.append(Vertex(prog, in_pos=[0.0, y + 0.05], in_color=[0.5, 0.5, 0.5]))
        return Mesh(ctx, vertices, prog, mgl.LINES)

    def step(self, scene, **kwargs):
        self.ctx.clear(0.0, 0.0, 0.0)

        w, h = self.width, self.height

        # Draw center line at origin
        self.prog['u_translate'].value = (0.0, 0.0)
        self.line_mesh.render()

        # Draw paddles
        for entity in ("left_paddle", "right_paddle"):
            pos = scene.fetch_component(entity, Position)
            if pos is None:
                continue
            # Convert to NDC (-1 to 1)
            nx = (pos["x"] / w) * 2 - 1
            ny = (pos["y"] / h) * 2 - 1
            self.prog['u_translate'].value = (nx, ny)
            self.paddle_mesh.render()

        # Draw ball
        ball = scene.fetch_component("ball", Position)
        if ball is not None:
            bx = (ball["x"] / w) * 2 - 1
            by = (ball["y"] / h) * 2 - 1
            self.prog['u_translate'].value = (bx, by)
            self.ball_mesh.render()

        pygame.display.flip()


# ============================================================
# SCENE
# ============================================================

class PongGLScene(Scene):
    def __init__(self, ctx: mgl.Context, prog: mgl.Program, width: int, height: int):
        super().__init__("pong", capacity=10)

        self.register_components([Position, Velocity, AABB, Score])
        self.render_system = GLRenderSystem(ctx, prog, width, height)
        self.systems = {
            "input": InputSystem(),
            "movement": MovementSystem(),
            "bounds": PaddleBoundsSystem(),
            "physics": BallPhysicsSystem(),
        }

    def step(self, dt: float = 1.0, **kwargs):
        # Run all systems
        for system in self.systems.values():
            system.step(self, dt=dt, **kwargs)
        # Run render
        self.render_system.step(self, **kwargs)

    def fetch_system(self, system_type):
        for system in self.systems.values():
            if isinstance(system, system_type):
                return system
        return None


# ============================================================
# CONTEXT
# ============================================================

class PongGLContext(Context):
    def __init__(self):
        pygame.init()

        if sys.platform == "darwin":
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        width, height = 800, 600
        config = Config(size=(width, height), fps=60)
        super().__init__()

        # OpenGL mode
        self.window = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        self.ctx = mgl.create_context()
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_pos;
                in vec3 in_color;
                out vec3 v_color;
                uniform vec2 u_translate;
                void main() {
                    gl_Position = vec4(in_pos + u_translate, 0.0, 1.0);
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

        scene = PongGLScene(self.ctx, self.prog, width, height)
        scene.initialize()

        # Add entities
        scene.add_entity("left_paddle", {
            Position: (50, height / 2),
            Velocity: (0, 0),
            AABB: (-10, -50, 20, 100),
        })
        scene.add_entity("right_paddle", {
            Position: (750, height / 2),
            Velocity: (0, 0),
            AABB: (-10, -50, 20, 100),
        })
        scene.add_entity("ball", {
            Position: (width / 2, height / 2),
            Velocity: (300, 0),
            AABB: (-10, -10, 20, 20),
        })
        scene.add_entity("score", {
            Score: (0, 0),
        })

        super().init_scenes({'pong': scene}, 'pong')
        super().init_config(config)
        super().init_time_manager()
        super().init_misc(caption="Pong - TamaJin ECS (OpenGL)")

    def step(self):
        for event in pygame.event.get():
            self.current_scene.fetch_system(InputSystem).handle_event(event)

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

        super().step()


if __name__ == "__main__":
    ctx = PongGLContext()
    ctx.run()