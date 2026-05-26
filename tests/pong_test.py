"""
Minimal Pong using TamaJin ECS systems.
"""

from abc import ABC, abstractmethod
import numpy as np
import pygame

from gameplay.physics.aabb import AABB
from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.scenes.scene import Scene
from gameplay.systems.system import System


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
            vel = scene.fetch(entity, Velocity)
            if vel is None:
                continue

            vel["x"] = 0
            vel["y"] = (
                (-speed if up in self.keys else 0) +
                (speed if down in self.keys else 0)
            )


class MovementSystem(System):

    def step(self, scene, dt=0.0, **kwargs):
        for _, pos, vel in scene.query(Position, Velocity):
            pos["x"] += vel["x"] * dt
            pos["y"] += vel["y"] * dt


class PaddleBoundsSystem(System):

    def step(self, scene, height=600, **kwargs):
        for entity in ("left_paddle", "right_paddle"):
            pos = scene.fetch(entity, Position)
            if pos is None:
                continue
            pos["y"] = np.clip(pos["y"], 50, height - 50)


class BallPhysicsSystem(System):

    def step(self, scene, width=800, height=600, **kwargs):
        ball_pos = scene.fetch("ball", Position)
        ball_vel = scene.fetch("ball", Velocity)
        score = scene.fetch("score", Score)

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
            pos = scene.fetch(paddle, Position)
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


class RenderSystem(System):

    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(None, 74)

    def step(self, scene, **kwargs):
        self.surface.fill((0, 0, 0))

        # Center line
        for y in range(0, 600, 40):
            pygame.draw.rect(
                self.surface,
                (255, 255, 255),
                (398, y, 4, 20)
            )

        # Paddles
        for entity in ("left_paddle", "right_paddle"):
            pos = scene.fetch(entity, Position)
            if pos is None:
                continue

            rect = pygame.Rect(
                int(pos["x"] - 10),
                int(pos["y"] - 50),
                20,
                100
            )
            pygame.draw.rect(self.surface, (255, 255, 255), rect)

        # Ball
        ball = scene.fetch("ball", Position)
        if ball is not None:
            pygame.draw.circle(
                self.surface,
                (255, 255, 255),
                (int(ball["x"]), int(ball["y"])),
                10
            )

        # Score
        score = scene.fetch("score", Score)
        if score is not None:
            for side, x_pos in [("left", 200), ("right", 560)]:
                text = self.font.render(str(score[side]), True, (255, 255, 255))
                self.surface.blit(text, (x_pos, 20))

        pygame.display.flip()


# ============================================================
# OOP ENGINE WRAPPER
# ============================================================

class PongEngine:

    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("TamaJin Pong")
        self.clock = pygame.time.Clock()
        self.running = False

        # ECS infrastructure dependencies
        self.scene = None
        self.input_system = None
        self.systems = []

        self._build_world()

    def _build_world(self):
        # Scene instantiation
        self.scene = Scene("pong", capacity=10)
        self.scene.register_component(Position, Position.schema)
        self.scene.register_component(Velocity, Velocity.schema)
        self.scene.register_component(AABB, AABB.schema)
        self.scene.register_component(Score, Score.schema)
        self.scene.initialize()

        # Entity construction
        paddles = {
            "left_paddle": (50, self.height / 2),
            "right_paddle": (750, self.height / 2),
        }
        for name, (x, y) in paddles.items():
            self.scene.add_entity(name, {
                Position: (x, y),
                Velocity: (0, 0),
                AABB: (-10, -50, 20, 100),
            })

        self.scene.add_entity("ball", {
            Position: (self.width / 2, self.height / 2),
            Velocity: (300, 0),
            AABB: (-10, -10, 20, 20),
        })

        self.scene.add_entity("score", {
            Score: (0, 0),
        })

        # Systems registration
        self.input_system = InputSystem()
        self.systems = [
            self.input_system,
            MovementSystem(),
            PaddleBoundsSystem(),
            BallPhysicsSystem(),
            RenderSystem(self.window),
        ]

    def run(self):
        self.running = True

        while self.running:
            dt = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                self.input_system.handle_event(event)
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            for system in self.systems:
                system.step(
                    self.scene,
                    dt=dt,
                    width=self.width,
                    height=self.height,
                )

        pygame.quit()


if __name__ == "__main__":
    game = PongEngine(width=800, height=600)
    game.run()