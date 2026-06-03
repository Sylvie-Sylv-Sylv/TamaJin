import pygame
from gameplay.scenes.scene import Scene
from gameplay.config.config import Config
from gameplay.time_manager.time_manager import TimeManager


class Context:
        def __init__(self, scenes: dict[str, Scene] = None, current_scene_id: str = 'default', config: Config = None, time_manager: TimeManager = None):
                if scenes is None:
                        scenes = {'default': Scene('default')}
                        
                if config is None:
                        config = Config()
                self.config = config

                if time_manager is None:
                        time_manager = TimeManager(config)
                self.time_manager = time_manager

                self.scenes = scenes
                self.current_scene_id = current_scene_id
        
        @property
        def current_scene(self):
                return self.scenes[self.current_scene_id]
        
        def step(self):
                dt = self.time_manager.step()
                self.scenes[self.current_scene_id].step(dt, substeps = self.config.substeps)