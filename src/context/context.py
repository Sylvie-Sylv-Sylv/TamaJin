from abc import abstractmethod, ABC

import pygame
from gameplay.scenes.scene import Scene
from gameplay.config.config import Config
from time_manager.time_manager import TimeManager


class Context(ABC):
    def __init__(self, **kwargs):
        pygame.init()

    def init_window(self, width: int = 800, height: int = 600):
        self.window = pygame.display.set_mode((800, 600))

    def init_scenes(
        self, scenes: dict[str, Scene] = None, current_scene_id: str = "default"
    ):
        if scenes is None:
            scenes = {"default": Scene("default")}
        self.scenes = scenes
        self.current_scene_id = current_scene_id

    def init_config(self, config: Config = None):
        if config is None:
            config = Config()
        self.config = config

    def init_time_manager(self, time_manager: TimeManager = None):
        if time_manager is None:
            time_manager = TimeManager(self.config)
        self.time_manager = time_manager

    def init_misc(self, caption: str = "TamaJin Game", **kwargs):
        pygame.display.set_caption(caption)
        self.running = None

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_id]

    def step(self):
        dt = self.time_manager.step()
        self.scenes[self.current_scene_id].step(dt, substeps=self.config.substeps)

    def run(self):
        self.running = True

        while self.running:
            self.step()

        self.running = False
        pygame.quit()
