from abc import abstractmethod
from typing import TypeVar, overload

from gameplay.general.vector2d import Vector2D

T = TypeVar("T")

class Scene:
        def __init__(self, name):
                self.name = name
                
                self.entities : set[str] = set()
                self.components : dict[str, dict[str, object]] = {}
        
        def register_component(self, component_name : str):
                if component_name not in self.components:
                        self.components[component_name] = {}
                else:
                        raise ValueError(f"Component {component_name} is already registered in the scene.")
        
        def add_entity(self, entity_id: str, **components: object):
                if entity_id in self.entities:
                        raise ValueError(f"Entity with id {entity_id} already exists in the scene.")

                self.entities.add(entity_id)

                for component_type in components:
                        component = components[component_type]
                        
                        if component_type not in self.components:
                                raise ValueError(f"Component type \"{component_type}\" is not registered.")

                        self.components[component_type][entity_id] = component
                
        def remove_entity(self, entity_id : str):
                if entity_id not in self.entities:
                        return

                self.entities.remove(entity_id)

                for storage in self.components.values():
                        storage.pop(entity_id, None)

        def fetch(
                self,
                entity_id: str,
                component_type: type[T]
        ) -> T | None:
                storage = self.components.get(component_type)

                if storage is None:
                        return None

                return storage.get(entity_id)

        def query(self, *component_types):
                component_maps = [
                        self.components[t]
                        for t in component_types
                ]

                smallest = min(component_maps, key=len)

                for entity in smallest:
                        if all(entity in storage for storage in component_maps):
                                yield (
                                        entity,
                                        *[
                                                storage[entity]
                                                for storage in component_maps
                                        ]
                                )