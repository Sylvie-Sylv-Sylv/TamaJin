import numpy as np

from gameplay.scenes.scene import Scene

class Position:
        schema = np.dtype([
                ("x", np.float32),
                ("y", np.float32)
        ], align=True)

class Velocity:
        schema = np.dtype([
                ("x", np.float32),
                ("y", np.float32)
        ], align=True)

class Health:
        schema = np.dtype([
                ("value", np.int32)
        ], align=True)

scene = Scene(
        "test_scene",
        capacity=128
)

# register component layouts
scene.register_component(
        Position,
        Position.schema
)

scene.register_component(
        Velocity,
        Velocity.schema
)

scene.register_component(
        Health,
        Health.schema
)

# finalize shared memory layout
scene.initialize()

# create entities
scene.add_entity(
        "player",
        {
                Position: (10.0, 20.0),
                Velocity: (1.5, 0.25),
                Health: (100,)
        }
)

scene.add_entity(
        "enemy_1",
        {
                Position: (50.0, 80.0),
                Velocity: (-0.5, 0.0),
                Health: (40,)
        }
)

scene.add_entity(
        "enemy_2",
        {
                Position: (100.0, 120.0),
                Velocity: (-1.0, 0.5),
                Health: (60,)
        }
)

# movement system
for entity, pos, vel in scene.query(
        Position,
        Velocity
):
        pos["x"] += vel["x"]
        pos["y"] += vel["y"]

        print(
                f"{entity} moved to "
                f"({pos['x']:.2f}, {pos['y']:.2f})"
        )

print()

# health system
for entity, health in scene.query(Health):
        health["value"] -= 10

        print(
                f"{entity} health = "
                f"{health['value']}"
        )

print()

# fetch single component
player_pos = scene.fetch_component(
        "player",
        Position
)

print(
        "player final position:",
        player_pos["x"],
        player_pos["y"]
)

print()

# remove entity
scene.remove_entity("enemy_1")

print("remaining entities:")

for entity, pos in scene.query(Position):
        print(
                entity,
                pos["x"],
                pos["y"]
        )