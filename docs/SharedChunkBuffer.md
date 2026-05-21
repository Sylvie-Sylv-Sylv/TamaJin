# SharedChunkBuffer: Memory-Efficient ECS Storage

A custom Entity Component System (ECS) storage implementation using contiguous NumPy memory with packed component columns for improved cache locality and iteration performance.

---

# Table of Contents

- [SharedChunkBuffer: Memory-Efficient ECS Storage](#sharedchunkbuffer-memory-efficient-ecs-storage)
- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [What This Actually Is](#what-this-actually-is)
- [The Problem: Python Object Memory](#the-problem-python-object-memory)
- [AoS vs SoA](#aos-vs-soa)
- [Array of Structures (AoS)](#array-of-structures-aos)
- [Structure of Arrays (SoA)](#structure-of-arrays-soa)
- [Why Pure SoA Still Has Problems](#why-pure-soa-still-has-problems)
- [Hybrid SoA/AoS Layout](#hybrid-soaaos-layout)
- [Single Shared Buffer](#single-shared-buffer)
- [Memory Layout](#memory-layout)
- [Zero-Copy NumPy Views](#zero-copy-numpy-views)
- [Cache Locality](#cache-locality)
- [Swap-Remove Deletion](#swap-remove-deletion)
- [Performance Characteristics](#performance-characteristics)
- [Usage Example](#usage-example)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)

---

# Overview

`SharedChunkBuffer` stores component data inside a single contiguous allocation and exposes typed NumPy array views into different regions of memory.

The implementation uses:

- contiguous packed memory
- Structure-of-Arrays (SoA) storage at the component level
- structured NumPy dtypes internally
- dense linear iteration
- O(1) swap-remove deletion

The goal is to avoid Python object overhead and improve iteration locality for ECS-style systems.

---

# What This Actually Is

This implementation is:

- a packed ECS table
- a columnar component storage system
- a single-buffer ECS layout

It is **not** a full archetype ECS.

A real archetype ECS:
- groups entities by exact component signatures
- dynamically moves entities between archetypes
- stores many chunk tables

This implementation instead uses:
- one shared table
- one packed memory allocation
- one component column per registered component type

So conceptually it behaves more like:
- a columnar database layout
- a packed ECS storage table

than a full archetype ECS.

---

# The Problem: Python Object Memory

A normal Python ECS often stores components as Python objects:

```python
positions = [
        Position(1, 2),
        Position(3, 4),
        Position(5, 6)
]
```

This creates:

```text
list -> pointers -> separate heap objects
```

Memory becomes fragmented because:
- Python lists store pointers
- objects are individually allocated
- fields are boxed Python objects
- memory locations are scattered across the heap

This causes:
- pointer chasing
- cache misses
- poor iteration performance
- high object overhead

---

# AoS vs SoA

# Array of Structures (AoS)

Traditional entity-oriented layout:

```text
[x y vx vy hp]
[x y vx vy hp]
[x y vx vy hp]
```

This is good for:
- accessing a single entity

But inefficient for:
- processing one component across many entities

because unrelated fields enter cache lines.

In native languages like C or C++, AoS is still contiguous memory:

```c
struct Position {
    float x;
    float y;
};

Position positions[1024];
```

So AoS is not inherently random memory access.

However, Python object-based AoS usually is fragmented due to heap allocation.

---

# Structure of Arrays (SoA)

Component-oriented layout:

```text
Position: [p0][p1][p2][p3]
Velocity: [v0][v1][v2][v3]
Health:   [h0][h1][h2][h3]
```

This improves:
- linear iteration
- cache locality
- sequential memory access

because all components of the same type are grouped together.

SoA is excellent when accessing:
- one component
- for many entities

Example:

```python
for position in positions:
        ...
```

because memory access becomes highly sequential.

---

# Why Pure SoA Still Has Problems

Pure SoA becomes less ideal when accessing:
- multiple components
- for many entities

Example:

```python
for i in range(entity_count):
        position = positions[i]
        velocity = velocities[i]
        health = healths[i]
```

Memory access pattern:

```text
[position block] -> [velocity block] -> [health block]
```

Even though each block is individually contiguous, iteration still jumps between separate memory regions.

Pure SoA optimizes:
- one dimension of locality

but not:
- cross-component locality

This implementation attempts to partially improve that by storing all component regions inside one large shared allocation.

The layout still remains component-oriented, but:
- all component columns now exist inside one contiguous buffer
- component regions are physically adjacent
- memory ownership becomes centralized
- chunk-style storage becomes possible

This creates a compromise between:
- SoA iteration efficiency
- reduced cross-component memory distance

without fully returning to AoS layouts.

---

# Hybrid SoA/AoS Layout

This implementation is not pure SoA.

The layout is:

```text
Position(x,y)[]
Velocity(x,y)[]
Health(value)[]
```

Each component column is SoA-style:

```text
[p0][p1][p2][p3]
```

but each individual structured dtype is internally AoS:

```text
[x y][x y][x y]
```

So:
- component storage is SoA
- field storage inside each dtype is AoS

This is a hybrid layout.

---

# Single Shared Buffer

Instead of allocating multiple independent arrays:

```python
position_array = np.zeros(...)
velocity_array = np.zeros(...)
health_array = np.zeros(...)
```

the implementation allocates one large contiguous buffer:

```python
self.buffer = np.zeros(total_bytes, dtype=np.uint8)
```

Then typed NumPy views are created into regions of that buffer.

Advantages:
- single allocation
- predictable ownership
- easier serialization
- contiguous component regions
- reduced allocation overhead
- physically adjacent component columns

The primary performance improvement still comes from:
- dense component columns
- sequential iteration
- avoiding Python objects

not necessarily from using one allocation alone.

---

# Memory Layout

Conceptual memory layout:

```text
┌──────────────────────────────────────┐
│ Position region                      │
│ [x y][x y][x y][x y]                 │
├──────────────────────────────────────┤
│ Velocity region                      │
│ [x y][x y][x y][x y]                 │
├──────────────────────────────────────┤
│ Health region                        │
│ [v][v][v][v]                         │
└──────────────────────────────────────┘
```

Each component region is contiguous.

All entities are tightly packed.

All component regions also live inside one shared allocation.

---

# Zero-Copy NumPy Views

The ECS creates typed NumPy views into the shared buffer:

```python
typed_view = np.ndarray(
        shape=(self.capacity,),
        dtype=dtype,
        buffer=self.buffer,
        offset=offset
)
```

Important:
- no memory is copied
- all arrays share the same backing allocation
- NumPy simply interprets bytes differently

This allows:
- packed storage
- efficient iteration
- low overhead access

---

# Cache Locality

Modern CPUs load memory in cache lines.

Sequential memory access is extremely important for performance.

This ECS improves locality because component data is stored contiguously:

```text
Position:
[p0][p1][p2][p3]
```

instead of:

```text
list -> object -> object -> object
```

Benefits:
- fewer cache misses
- better hardware prefetching
- sequential iteration
- lower pointer overhead

Cross-component locality is also partially improved because:
- all component columns exist inside one allocation
- component regions are adjacent in memory
- memory ownership is centralized

However, this still is not equivalent to true AoS or archetype chunk locality.

Accessing:

```python
Position[i]
Velocity[i]
```

still jumps between component regions.

So this layout optimizes:
- component iteration

more than:
- single-entity locality

while still reducing memory fragmentation between columns.

---

# Swap-Remove Deletion

Removing entities uses swap-remove:

```python
array[index] = array[last_index]
```

instead of shifting all elements.

Example:

Before:

```text
0: player
1: enemy
2: npc
3: boss
```

Remove `"enemy"`:

```text
0: player
1: boss
2: npc
```

Advantages:
- O(1) deletion
- dense packed arrays
- no holes in memory

The tradeoff:
- entity ordering is unstable

---

# Performance Characteristics

| Operation | Complexity |
|---|---|
| Add entity | O(1) |
| Remove entity | O(1) |
| Fetch component | O(1) |
| Query iteration | O(n) |
| Memory layout | Dense contiguous |
| Cache locality | Good |
| Python overhead | Reduced |

Compared to Python object ECS:
- dramatically fewer allocations
- less pointer chasing
- much better iteration performance

Compared to native C++ ECS:
- still slower due to Python runtime overhead
- but significantly more memory efficient than Python object systems

---

# Usage Example

```python
import numpy as np

from gameplay.scenes.scene import Scene

class Position:
        pass

class Velocity:
        pass

class Health:
        pass

PositionData = np.dtype([
        ("x", np.float32),
        ("y", np.float32)
], align=True)

VelocityData = np.dtype([
        ("x", np.float32),
        ("y", np.float32)
], align=True)

HealthData = np.dtype([
        ("value", np.int32)
], align=True)

scene = Scene(
        "game_world",
        capacity=1024
)

scene.register_component(
        Position,
        PositionData
)

scene.register_component(
        Velocity,
        VelocityData
)

scene.register_component(
        Health,
        HealthData
)

scene.initialize()

scene.add_entity(
        "player",
        {
                Position: (10.0, 20.0),
                Velocity: (1.5, 0.25),
                Health: (100,)
        }
)

for entity, pos, vel in scene.query(
        Position,
        Velocity
):
        pos["x"] += vel["x"]
        pos["y"] += vel["y"]

        print(entity, pos["x"], pos["y"])
```

---

# Limitations

Current limitations:

- fixed capacity
- single storage table
- no real archetype grouping
- no dynamic component add/remove
- structured dtypes are internally AoS
- not fully SIMD-optimal
- entity IDs still use Python dictionaries

The implementation optimizes:
- packed component iteration

not:
- dynamic ECS flexibility

---

# Future Improvements

Possible future improvements:

- real archetype storage
- chunk chains
- dynamic table migration
- pure SoA field splitting
- SIMD-friendly layouts
- multithreaded iteration
- Numba acceleration
- generational entity IDs
- sparse archetype queries
- parallel system execution
- chunk streaming
- serialization support