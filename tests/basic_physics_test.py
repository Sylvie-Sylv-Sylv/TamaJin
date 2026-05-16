from sklearn import tree

from gameplay.physics.position import Position
from gameplay.physics.velocity import Velocity
from gameplay.physics.force import Force
from gameplay.physics.mass import Mass
from gameplay.scene import Scene
from gameplay.systems.verlet_integrator import VerletIntegrator
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.runtime.quad_tree import QuadTree
from gameplay.physics.aabb import AABB

class TestScene(Scene):
        def __init__(self):
                super().__init__("test_scene")
                
                self.tree = QuadTree(AABB(0, 0, 100, 100))
                
                self.register_component(Position)
                self.register_component(Velocity)
                self.register_component(Force)
                self.register_component(Mass)
                self.register_component(AABB)
        
        def step(self):
                VerletIntegrator.step(self, dt = 1.0)
                QuadTreeInserter.step(self)

def main():
        scene = TestScene()
        
        scene.add_entity("entity_1", Position(0, 0), Velocity(1, 0), Force(1, 0), Mass(1.0), AABB(100, 100, 23, 32))
        
        scene.step()

        print(scene.tree.query( AABB(90, 90, 100, 100)))
        
        print(f"Position: {scene.components[Position].get('entity_1', None)}")
        print(f"Velocity: {scene.components[Velocity].get('entity_1', None)}")
        print(f"Force: {scene.components[Force].get('entity_1', None)}")
        print(f"Mass: {scene.components[Mass].get('entity_1', None).value}")

if __name__ == "__main__":
        main()