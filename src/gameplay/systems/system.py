from abc import abstractmethod

from gameplay.scenes.scene import Scene

class System:
        @staticmethod
        @abstractmethod
        def step(scene : Scene, *args, **kwargs):
                raise NotImplementedError("Subclasses must implement the step method.")