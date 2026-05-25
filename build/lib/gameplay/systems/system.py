from abc import abstractmethod

from gameplay.scenes.scene import Scene

class System:
        """
        Base class for all ECS systems.
        Systems contain the logic that processes entities possessing specific component signatures.
        """
        @staticmethod
        @abstractmethod
        def step(scene : Scene, *args, **kwargs):
                """
                Updates the state of the scene.

                :param scene: The active Scene object containing entities and components.
                :param args: Additional positional arguments for system logic.
                :param kwargs: Additional keyword arguments for system logic.
                """
                raise NotImplementedError("Subclasses must implement the step method.")