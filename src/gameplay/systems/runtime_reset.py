from gameplay.systems.system import System


class RuntimeReset(System):
        @staticmethod
        def step(scene):
                scene.broad_collision_pairs.clear()
                scene.narrow_collision_pairs.clear()
                scene.narrow_collision_mtv.clear()