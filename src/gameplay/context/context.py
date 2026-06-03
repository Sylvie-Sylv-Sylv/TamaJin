import pygame
from gameplay.scenes.scene import Scene
from gameplay.config.config import Config


class Context:
        def __init__(self, scenes: dict[str, Scene] = None, current_scene: str = 'default', config: Config = None):
                if scenes is None:
                        scenes = {'default': Scene('default')}
                if config is None:
                        config = Config()
                self.clock = pygame.time.Clock()
                self.config = config
                
                self.scenes = scenes
                self.current_scene = current_scene
        
        def step(self):
                dt = self.clock.tick(self.config.fps)
                self.scenes[self.current_scene].step(dt / 1000.0, substeps = self.config.substeps)