import pygame


class TimeManager:
    def __init__(self, config, clock: pygame.time.Clock = None):
        if clock is None:
            clock = pygame.time.Clock()
        self.clock = clock
        self.config = config

    def step(self) -> float:
        return self.clock.tick(self.config.fps) / 1000.0
