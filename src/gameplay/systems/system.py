from abc import abstractmethod

from gameplay.scene import Scene

class System:
        @staticmethod
        @abstractmethod
        def step(scene : Scene, *args, **kwargs):
                raise NotImplementedError("Subclasses must implement the step method.")