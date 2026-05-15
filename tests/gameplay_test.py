from src.gameplay.components.vector2d import Vector2D
from src.gameplay.scene import Scene
from src.gameplay.systems.verlet_first import VerletFirst
from src.gameplay.systems.verlet_second import VerletSecond
from src.gameplay.systems.verlet_third import VerletThird

class TestScene(Scene):
        def __init__(self):
                super().__init__("test_scene")
        
        def step(self):
                for entity_id in self.entities:
                        if [position := self.position.get(entity_id, None),
                            velocity := self.velocity.get(entity_id, None),
                            old_acceleration := self.old_acceleration.get(entity_id, None),
                            new_acceleration := self.new_acceleration.get(entity_id, None)].count(None) == 0:
                                VerletFirst.step(position, velocity, old_acceleration, 1)
                                VerletSecond.step(old_acceleration, new_acceleration, 1)
                                VerletThird.step(velocity, old_acceleration, new_acceleration, 1)

def main():
        scene = TestScene()
        
        scene.add_entity("entity_1", position = Vector2D(0, 0), velocity = Vector2D(1, 0), old_acceleration = Vector2D(0, 0), new_acceleration = Vector2D(0, -9.8))
        scene.step()
        
        print(f"Position: {scene.position.get('entity_1', None)}")
        print(f"Velocity: {scene.velocity.get('entity_1', None)}")
        print(f"Old Acceleration: {scene.old_acceleration.get('entity_1', None)}")
        print(f"New Acceleration: {scene.new_acceleration.get('entity_1', None)}")
        
if __name__ == "__main__":
        main()