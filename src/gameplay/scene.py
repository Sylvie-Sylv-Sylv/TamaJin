from abc import abstractmethod

from gameplay.general.vector2d import Vector2D

class Scene:
        def __init__(self, name):
                self.name = name
                
                self.entities : set[str] = set()
                self.components : dict[type, dict[str, object]] = {}
        
        def register_component(self, component_name : type):
                if component_name not in self.components:
                        self.components[component_name] = {}
                else:
                        raise ValueError(f"Component {component_name} is already registered in the scene.")
        
        def add_entity(self, entity_id: str, *components: object):
                if entity_id in self.entities:
                        raise ValueError(f"Entity with id {entity_id} already exists in the scene.")

                self.entities.add(entity_id)

                for component in components:
                        component_type = type(component)

                        if component_type not in self.components:
                                raise ValueError(f"Component type {component_type.__name__} is not registered.")

                        self.components[component_type][entity_id] = component
                
        def remove_entity(self, entity_id : str):
                if entity_id not in self.entities:
                        return

                self.entities.remove(entity_id)

                for storage in self.components.values():
                        storage.pop(entity_id, None)

        def query(self, *component_types):
                component_maps = [
                        self.components[t]
                        for t in component_types
                ]

                entity_sets = [
                        set(storage.keys())
                        for storage in component_maps
                ]

                matching_entities = set.intersection(*entity_sets)

                for entity in matching_entities:
                        yield(entity,
                              *[
                                      storage[entity]
                                      for storage in component_maps
                              ]
                        )

        @abstractmethod
        def step():
                raise NotImplementedError("Scene step method is not implemented yet.")