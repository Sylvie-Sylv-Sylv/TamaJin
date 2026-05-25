from gameplay.systems.system import System


class RuntimeReset(System):
        @staticmethod
        def step(scene):
                if hasattr(scene, 'broad_collision_pairs'): scene.broad_collision_pairs.clear()
                if hasattr(scene, 'narrow_collision_pairs'): scene.narrow_collision_pairs.clear()
                if hasattr(scene, 'narrow_collision_mtv'): scene.narrow_collision_mtv.clear()
                if hasattr(scene, 'narrow_collision_contacts'): scene.narrow_collision_contacts.clear()