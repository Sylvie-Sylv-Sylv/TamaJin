from gameplay.systems.system import System


class CollisionSolverPos(System):
        @staticmethod
        def step(scene, dt):
                for entity_a, entity_b in scene.narrow_collision_pairs:
                        mtv = scene.narrow_collision_mtv[(entity_a, entity_b)]
                        
                        if (mass_a := scene.fetch(entity_a, 'mass')) \
                           and (mass_b := scene.fetch(entity_b, 'mass')):
                                total_inv = mass_a.inv + mass_b.inv
                                   
                                if position_a := scene.fetch(entity_a, 'position'):
                                        position_a += mtv * mass_a.inv / total_inv * 0.999
                                if position_b := scene.fetch(entity_b, 'position'):
                                        position_b -= mtv * mass_b.inv / total_inv * 0.999