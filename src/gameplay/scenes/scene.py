from __future__ import annotations
from typing import TypeVar

import numpy as np

from build.lib.gameplay.systems.system import System

T = TypeVar("T")

class SharedChunkBuffer:
        """
        A memory-efficient storage container for ECS components.
        
        It uses a single contiguous NumPy byte buffer to store all component data,
        providing typed views into specific regions. This layout maximizes cache 
        locality and minimizes Python object overhead during system iteration.
        """
        def __init__(self, capacity: int):
                self.capacity = capacity
                self.size = 0

                self.component_offsets: dict[type, int] = {}
                self.component_dtypes: dict[type, np.dtype] = {}
                self.component_arrays: dict[type, np.ndarray] = {}

                self.entity_to_index: dict[str, int] = {}
                self.index_to_entity: list[str] = []

                self.buffer: np.ndarray | None = None

        def register_components(
                self,
                component_layouts: dict[type, np.dtype]
        ):
                """
                Allocates the shared buffer and calculates memory offsets for each component type.
                
                :param component_layouts: A mapping of component classes to their 
                                          NumPy structured dtypes.
                """
                total_bytes = 0

                # calcualte byte offsets for every component
                for component_type, dtype in component_layouts.items():
                        dtype = np.dtype(dtype)

                        alignment = dtype.alignment

                        # align current offset
                        if total_bytes % alignment != 0:
                                total_bytes += (
                                        alignment -
                                        (total_bytes % alignment)
                                )

                        self.component_offsets[
                                component_type
                        ] = total_bytes

                        self.component_dtypes[
                                component_type
                        ] = dtype

                        total_bytes += (
                                dtype.itemsize * self.capacity
                        )

                # single contigious allocation
                self.buffer = np.zeros(
                        total_bytes,
                        dtype=np.uint8
                )

                # create typed array views into the shared buffer
                for component_type, dtype in component_layouts.items():
                        dtype = np.dtype(dtype)

                        offset = self.component_offsets[
                                component_type
                        ]

                        typed_view = np.ndarray(
                                shape=(self.capacity,),
                                dtype=dtype,
                                buffer=self.buffer,
                                offset=offset
                        )

                        self.component_arrays[
                                component_type
                        ] = typed_view

        def add_entity(
                self,
                entity_id: str,
                components: dict[type, object]
        ):
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

                # write component data into packed arrays
                for component_type, value in components.items():
                        self.component_arrays[
                                component_type
                        ][index] = value

        def remove_entity(self, entity_id: str):
                index = self.entity_to_index.pop(entity_id)

                last_index = self.size - 1
                last_entity = self.index_to_entity[last_index]

                # swap remove keeps memory tightly packed
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
                component_type: type
        ):
                index = self.entity_to_index.get(entity_id)

                if index is None:
                        return None

                array = self.component_arrays.get(
                        component_type
                )

                if array is None:
                        return None

                return array[index]

        def query(self, *component_types):
                """
                Yields entity IDs and requested components for all entities possessing them.
                
                This provides high-performance linear iteration over packed memory.
                """

                # gather component columns for linear iteration
                arrays = [
                        self.component_arrays[component_type]
                        for component_type in component_types
                ]

                for i in range(self.size):
                        yield (
                                self.index_to_entity[i],
                                *[
                                        array[i]
                                        for array in arrays
                                ]
                        )

class Scene:
        def __init__(
                self,
                name,
                capacity=1024
        ):
                self.name = name

                self.entities: set[str] = set()

                # archetype-like shared chunk storage
                self.chunk = SharedChunkBuffer(capacity)

                self.pending_components: dict[
                        type,
                        np.dtype
                ] = {}
                
                self.systems: dict[str, System] = {}

                self.initialized = False

        def register_component(
                self,
                component_type: type,
                dtype
        ):
                if self.initialized:
                        raise RuntimeError(
                                "Cannot register components after initialization."
                        )

                self.pending_components[
                        component_type
                ] = np.dtype(dtype)
        
        def register_system(self, system: System):
                self.systems[system.__class__.__name__] = system

        def initialize(self):
                # finalize layout and allocate shared memroy
                self.chunk.register_components(
                        self.pending_components
                )

                self.initialized = True

        def add_entity(
                self,
                entity_id: str,
                components: dict[type, object]
        ):
                if not self.initialized:
                        raise RuntimeError(
                                "Scene.initialize() must be called first."
                        )

                self.entities.add(entity_id)

                self.chunk.add_entity(
                        entity_id,
                        components
                )

        def remove_entity(self, entity_id: str):
                if entity_id not in self.entities:
                        return

                self.entities.remove(entity_id)
                self.chunk.remove_entity(entity_id)

        def fetch_component(
                self,
                entity_id: str,
                component_type: type
        ):
                return self.chunk.fetch(
                        entity_id,
                        component_type
                )
        
        def fetch_system(self, system_type: type):
                return self.systems.get(system_type.__name__)

        def query(self, *component_types):
                yield from self.chunk.query(
                        *component_types
                )