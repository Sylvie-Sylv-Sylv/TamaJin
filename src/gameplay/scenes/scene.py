from __future__ import annotations

from typing import Any, Iterator, TypeVar

import numpy as np
from numpy.typing import NDArray

from gameplay.systems.system import System

T = TypeVar("T")


class SharedChunkBuffer:
    """
    A memory-efficient storage container for ECS components.
    """

    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        self.size: int = 0

        self.component_offsets: dict[type, int] = {}
        self.component_dtypes: dict[type, np.dtype[Any]] = {}
        self.component_arrays: dict[type, NDArray[Any]] = {}

        self.entity_to_index: dict[str, int] = {}
        self.index_to_entity: list[str] = []

        self.buffer: NDArray[np.uint8] | None = None

    def register_components(
        self,
        component_layouts: dict[type, np.dtype[Any]]
    ) -> None:
        total_bytes = 0

        for component_type, dtype in component_layouts.items():
            dtype = np.dtype(dtype)

            alignment = dtype.alignment

            if total_bytes % alignment != 0:
                total_bytes += (
                    alignment -
                    (total_bytes % alignment)
                )

            self.component_offsets[component_type] = total_bytes
            self.component_dtypes[component_type] = dtype

            total_bytes += dtype.itemsize * self.capacity

        self.buffer = np.zeros(
            total_bytes,
            dtype=np.uint8
        )

        for component_type, dtype in component_layouts.items():
            dtype = np.dtype(dtype)

            offset = self.component_offsets[component_type]

            typed_view: NDArray[Any] = np.ndarray(
                shape=(self.capacity,),
                dtype=dtype,
                buffer=self.buffer,
                offset=offset
            )

            self.component_arrays[component_type] = typed_view

    def add_entity(
        self,
        entity_id: str,
        components: dict[type, object]
    ) -> None:
        if self.size >= self.capacity:
            raise MemoryError("Chunk full")

        if entity_id in self.entity_to_index:
            raise ValueError(
                f"Entity {entity_id} already exists."
            )

        index = self.size
        self.size += 1

        self.entity_to_index[entity_id] = index
        self.index_to_entity.append(entity_id)

        for component_type, value in components.items():
            self.component_arrays[component_type][index] = value

    def remove_entity(self, entity_id: str) -> None:
        index = self.entity_to_index.pop(entity_id)

        last_index = self.size - 1
        last_entity = self.index_to_entity[last_index]

        if index != last_index:
            for array in self.component_arrays.values():
                array[index] = array[last_index]

            self.entity_to_index[last_entity] = index
            self.index_to_entity[index] = last_entity

        self.index_to_entity.pop()
        self.size -= 1

    def fetch(
        self,
        entity_id: str,
        component_type: type[T]
    ) -> T | None:
        index = self.entity_to_index.get(entity_id)

        if index is None:
            return None

        array = self.component_arrays.get(component_type)

        if array is None:
            return None

        return array[index]

    def query(
        self,
        *component_types: type
    ) -> Iterator[tuple[Any, ...]]:
        arrays = [
            self.component_arrays[component_type]
            for component_type in component_types
        ]

        for i in range(self.size):
            yield (
                self.index_to_entity[i],
                *(
                    array[i]
                    for array in arrays
                )
            )


class Scene:
    def __init__(
        self,
        name: str,
        capacity: int = 1024
    ) -> None:
        self.name: str = name

        self.entities: set[str] = set()

        self.chunk: SharedChunkBuffer = SharedChunkBuffer(
            capacity
        )

        self.pending_components: dict[
            type,
            np.dtype[Any]
        ] = {}

        self.systems: dict[str, System] = {}

        self.initialized: bool = False

    def register_component(
        self,
        component_type: type
    ) -> None:
        if self.initialized:
            raise RuntimeError(
                "Cannot register components after initialization."
            )

        self.pending_components[
            component_type
        ] = np.dtype(component_type.schema)

    def register_components(
        self,
        component_types: list[type]
    ) -> None:
        for component_type in component_types:
            self.register_component(component_type)

    def register_system(
        self,
        system: System
    ) -> None:
        self.systems[
            system.__class__.__name__
        ] = system

    def register_systems(
        self,
        systems: list[System]
    ) -> None:
        for system in systems:
            self.register_system(system)

    def initialize(self) -> None:
        self.chunk.register_components(
            self.pending_components
        )

        self.initialized = True

    def add_entity(
        self,
        entity_id: str,
        components: dict[type, object]
    ) -> None:
        if not self.initialized:
            raise RuntimeError(
                "Scene.initialize() must be called first."
            )

        self.entities.add(entity_id)

        self.chunk.add_entity(
            entity_id,
            components
        )

    def remove_entity(
        self,
        entity_id: str
    ) -> None:
        if entity_id not in self.entities:
            return

        self.entities.remove(entity_id)
        self.chunk.remove_entity(entity_id)

    def fetch_component(
        self,
        entity_id: str,
        component_type: type[T]
    ) -> T | None:
        return self.chunk.fetch(
            entity_id,
            component_type
        )

    def fetch_system(
        self,
        system_type: type[System]
    ) -> System | None:
        return self.systems.get(
            system_type.__name__
        )

    def query(
        self,
        *component_types: type
    ) -> Iterator[tuple[Any, ...]]:
        yield from self.chunk.query(
            *component_types
        )