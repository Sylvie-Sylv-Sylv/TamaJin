from gameplay.systems.system import System
from gameplay.physics.mass import Mass
from gameplay.physics.position import Position


class CollisionSolverPos(System):
        @staticmethod
        def step(scene, dt):
                for entity_a, entity_b in scene.narrow_collision_pairs:
                        mtv = scene.narrow_collision_mtv[(entity_a, entity_b)]
                        
                        if (mass_a := scene.fetch(entity_a, Mass)) is not None \
                           and (mass_b := scene.fetch(entity_b, Mass)) is not None:
                                total_inv = mass_a['inv'] + mass_b['inv']
                                   
                                if (position_a := scene.fetch(entity_a, Position)) is not None:
                                        position_a['x'] += mtv.x * mass_a['inv'] / total_inv * 0.999
                                        position_a['y'] += mtv.y * mass_a['inv'] / total_inv * 0.999
                                if (position_b := scene.fetch(entity_b, Position)) is not None:
                                        position_b['x'] -= mtv.x * mass_b['inv'] / total_inv * 0.999
                                        position_b['y'] -= mtv.y * mass_b['inv'] / total_inv * 0.999