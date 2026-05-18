from abc import abstractmethod

from gameplay.scenes.sparse_scene import SparseScene

class System:
        @staticmethod
        @abstractmethod
        def step(scene : SparseScene, *args, **kwargs):
                raise NotImplementedError("Subclasses must implement the step method.")