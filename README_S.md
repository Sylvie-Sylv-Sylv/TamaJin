# TamaJin

High-performance game framework in Python. ECS + audio + physics + shader graphs.

## Philosophy

1. **Performance** — SharedChunkBuffer for cache locality
2. **Clean code** — Numpy dtypes, type hints, modular
3. **Observability** — 7-level logging
4. **Extendable** — Components, systems, nodes
5. **Configurable** — Audio buses, collision pipeline
6. **Adaptive** — Prototype to product

## Features

- ECS with SharedChunkBuffer
- Bus-based audio mixing
- Rigidbody physics (Verlet + SAT)
- Python-defined shader graphs

## Architecture

```
audio/       — Audio mixing
gameplay/    — Physics, ECS, logging
graphics/    — Mesh, texture, shaders
```

## Dependencies

- numpy, pygame, moderngl, miniaudio, PIL