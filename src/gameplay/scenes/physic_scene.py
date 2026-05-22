from typing import Any

from gameplay.general.vector2d import Vec2
from gameplay.physics.aabb import AABB
from gameplay.physics.angular_velocity import AngularVelocity
from gameplay.physics.new_force import NewForce
from gameplay.physics.old_force import OldForce
from gameplay.physics.mass import Mass
from gameplay.physics.polygon import Polygon
from gameplay.physics.position import Position
from gameplay.physics.rotation import Rotation
from gameplay.physics.velocity import Velocity
from gameplay.runtime.quad_tree import QuadTree
from gameplay.scenes.scene import Scene
from gameplay.systems.broad_phase_collision import BroadPhaseCollision
from gameplay.systems.collision_solver_pos import CollisionSolverPos
from gameplay.systems.collision_solver_vel import CollisionSolverVel
from gameplay.systems.narrow_phase_collision import NarrowPhaseCollision
from gameplay.systems.quad_tree_inserter import QuadTreeInserter
from gameplay.systems.runtime_reset import RuntimeReset
from gameplay.systems.verlet_first import VerletFirst
from gameplay.systems.verlet_second import VerletSecond

class PhysicScene(Scene):
        """
        An extension of Scene that manages a specialized physics pipeline, 
        including spatial partitioning and collision resolution manifolds.
        """
        def __init__(self):
                super().__init__("basic_scene")
                
                self.tree: QuadTree = QuadTree(AABB(0, 0, 800, 800))
                self.broad_collision_pairs: set[tuple[str, str]] = set()
                self.narrow_collision_pairs: set[tuple[str, str]] = set() # (entity_a, entity_b)
                self.narrow_collision_mtv: dict[tuple[str, str], Vec2] = {} # (entity_a, entity_b) -> MTV vector
                self.narrow_collision_contacts: dict[tuple[str, str], list[Vec2]] = {} # (entity_a, entity_b) -> list of contact points
                
                self.register_component(Position, Position.schema)
                self.register_component(Velocity, Velocity.schema)
                self.register_component(OldForce, OldForce.schema)
                self.register_component(NewForce, NewForce.schema)
                self.register_component(Rotation, Rotation.schema)
                self.register_component(AngularVelocity, AngularVelocity.schema)
                self.register_component(Mass, Mass.schema)
                self.register_component(AABB, AABB.schema)
                self.register_component(Polygon, object)
        
        def step(self, dt: float = 1.0, substeps: int = 4):
                """
                Executes a single physics frame.
                
                The pipeline follows a specific order: Integration (Verlet) -> Broadphase -> 
                Narrowphase -> Position Correction -> Acceleration Update -> Velocity Correction.

                :param substeps: Number of times to run the physics loop per frame. 
                                 Higher values increase stability at the cost of CPU.
                """
                sub_dt = dt / substeps

                for _ in range(substeps):
                        RuntimeReset.step(self)
                        VerletFirst.step(self, dt = sub_dt)
                        self.tree.clear()
                        QuadTreeInserter.step(self)
                        BroadPhaseCollision.step(self)
                        NarrowPhaseCollision.step(self)
                        CollisionSolverPos.step(self, dt = sub_dt)
                        VerletSecond.step(self, dt = sub_dt)
                        CollisionSolverVel.step(self, dt = sub_dt)

        def add_physics_entity(
                self, 
                entity_id: str, 
                pos: Vec2, 
                mass: float = 1.0, 
                poly: Polygon = None,
                **kwargs
        ):
                """
                Convenience helper to create a standard physics entity with the correct 
                buffer-aligned data structures.
                """
                components = {
                        Position: (pos[0], pos[1]),
                        Velocity: kwargs.get('velocity', (0.0, 0.0)),
                        OldForce: (0.0, 0.0),
                        NewForce: (0.0, 0.0),
                        Rotation: (kwargs.get('rotation_val', 0.0),),
                        AngularVelocity: (kwargs.get('angular_vel', 0.0),),
                        Mass: (mass, 1.0 / mass if mass != 0 else 0.0)
                }

                if poly:
                        components[Polygon] = poly
                        components[AABB] = poly.compute_aabb().to_tuple()
                elif 'aabb' in kwargs:
                        components[AABB] = kwargs['aabb'].to_tuple()

                # Add any additional custom components provided
                for comp_type, data in kwargs.items():
                        if isinstance(comp_type, type):
                                components[comp_type] = data

                self.add_entity(entity_id, components)