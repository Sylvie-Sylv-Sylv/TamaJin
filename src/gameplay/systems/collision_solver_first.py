from gameplay.physics.position import Position
from gameplay.systems.system import System


class CollisionSolverFirst(System):
        @staticmethod
        def step(scene, dt):
                print(1)
                for entity_a, entity_b in scene.narrow_collision_pairs:
                        mtv = scene.narrow_collision_mtv[(entity_a, entity_b)]
                        
                        if position_a := scene.fetch(entity_a, Position):
                                position_a += mtv * 0.5 * 1.0001
                        if position_b := scene.fetch(entity_b, Position):
                                position_b -= mtv * 0.5