# TamaJin

A high-performance game development framework written in Python, built around ECS architecture, custom audio mixing, rigidbody physics, and a Python-defined shader graph system.

---

## Philosophy

TamaJin is built on six foundational principles that guide every design decision:

### 1. Performance Through Memory Design

The heart of TamaJin is the **SharedChunkBuffer** — a single contiguous NumPy byte buffer that stores all ECS component data. This design isn't about theoretical optimization; it's about what happens when you iterate over thousands of entities every frame. By keeping component data contiguous in memory, we maximize cache hits and minimize the overhead that comes from Python object references. Every component is stored as a numpy dtype, giving us typed views into specific memory regions without the indirection of dictionaries or objects.

### 2. Codebase Hygiene

A codebase that grows over years needs rules that everyone follows without thinking about them. We maintain clean and consistent code through strict conventions: numpy dtypes for all physics components, type hints everywhere, and modular architecture with clear separation between audio, gameplay, and graphics. When code looks familiar, you can read it faster, debug it quicker, and extend it with confidence.

### 3. Observability First

When something breaks in production, you need to understand what happened. TamaJin's logging system provides seven levels of verbosity — from TRACE for detailed execution flow to ASSERT for critical failures. Every system logs its actions. Every error carries context. We believe that good logging isn't about catching exceptions; it's about making the system's behavior visible before things go wrong.

### 4. Growth Without Rewriting

Games evolve. Features get added, removed, and added again. TamaJin's architecture is designed to grow with your project. New components? Just define a numpy dtype and register it. New systems? Extend the System base class. New shader operations? Compose nodes together. The system doesn't fight you when you need to extend it.

### 5. Configuration Without Compromise

Different games have different needs. An indie prototype might skip complex audio mixing. A shipped product needs every optimization. TamaJin gives you control over every layer — from the audio bus hierarchy to the collision pipeline to the shader compilation. Build what you need, skip what you don't.

### 6. Architecture That Adapts

The same codebase should support a quick prototype and a polished product. Switch between broad and narrow phase collision strategies. Choose Verlet first or second order integration. Configure the quad tree depth for your scene size. TamaJin's systems are composable, letting you build the architecture that fits your game.

---

## Current Features

### Optimized ECS System

The Entity-Component-System architecture uses a SharedChunkBuffer for high-performance component storage. Components are stored as numpy dtypes, providing typed views into contiguous memory regions. Query the scene for entities with specific component combinations and iterate with minimal overhead.

### Audio System with Buses

A complete audio pipeline with bus-based mixing. Load WAV files, route them through buses, apply volume and pitch transformations, and mix everything to a final output. The system supports looping voices, multiple output channels, and real-time parameter changes.

### Rigidbody Physics

Full rigidbody physics with Verlet integration. Two-pass integration (first order for position, second order for velocity) provides stable simulation. The collision pipeline uses broad phase (quad tree) and narrow phase (SAT polygon) detection, with separate position and velocity solvers.

### Python-Defined Shader Graphs

Write shaders in Python, not GLSL. Define input variables, compose operations as nodes, and generate GLSL automatically. The shader graph system provides type safety, composition, and a clear visual structure for your rendering pipeline.

---

## Architecture

```
TamaJin/
├── audio/                   # Audio mixing and playback
│   ├── audio_bus.py        # AudioBus mixing hierarchy
│   ├── audio_clip.py      # Audio sample container
│   ├── audio_voice.py    # Voice playback
│   ├── master_audio_bus.py # Final output generator
│   ├── root_audio_bus.py # Base bus with voices
│   └── utils.py         # WAV loading
│
├── gameplay/
│   ├── general/          # Core utilities
│   │   ├── child.py     # Entity relationship
│   │   ├── parent.py   # Entity relationship
│   │   └── vector2d.py # 2D vector math
│   │
│   ├── logging/          # Custom logging
│   │   ├── handlers.py # Console/file handlers
│   │   ├── levels.py  # Log levels
│   │   └── logger.py  # Logger API
│   │
│   ├── physics/         # Physics components
│   │   ├── aabb.py    # Axis-aligned box
│   │   ├── angular_velocity.py
│   │   ├── mass.py    # Mass with inverse
│   │   ├── new_force.py
│   │   ├── old_force.py
│   │   ├── polygon.py # Convex polygon
│   │   ├── position.py
│   │   ├── rotation.py
│   │   ├── shape.py   # Shape base
│   │   └── velocity.py
│   │
│   ├── runtime/         # Spatial partitioning
│   │   ├── quad_node.py
│   │   └── quad_tree.py
│   │
│   ├── scenes/         # ECS management
│   │   ├── scene.py    # Base scene
│   │   └── physic_scene.py
│   │
│   └── systems/        # ECS systems
│       ├── broad_phase_collision.py
│       ├── collision_solver_pos.py
│       ├── collision_solver_vel.py
│       ├── narrow_phase_collision.py
│       ├── quad_tree_inserter.py
│       ├── runtime_reset.py
│       ├── system.py    # System base
│       ├── verlet_first.py
│       └── verlet_second.py
│
└── graphics/
    ├── mesh.py         # ModernGL mesh
    ├── texture.py     # Texture loading
    ├── texture_array.py
    ├── vertex.py    # Shader attributes
    └── shader_graph/ # GLSL builder
        ├── builder/
        ├── nodes/
        ├── program/
        └── vars/
```

---

## Dependencies

- `numpy` — Component storage and vector math
- `pygame` — Physics rendering and windowing
- `moderngl` — OpenGL rendering
- `miniaudio` — WAV file loading
- `PIL` — Image loading for textures

---

## License

MIT