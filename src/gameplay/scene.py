from abc import abstractmethod

from src.gameplay.components.vector2d import Vector2D
from src.gameplay.components.component import Component

class Scene:
        def __init__(self, name):
                self.name = name
                
                self.entities : set[str] = set()
                
                self.position = {}
                self.velocity = {}
                self.old_acceleration = {}
                self.new_acceleration = {}
        
        def add_entity(self, entity_id : str, position : Vector2D = None, velocity : Vector2D = None, old_acceleration : Vector2D = None, new_acceleration : Vector2D = None):
                if entity_id in self.position:
                        raise ValueError(f"Entity with id {entity_id} already exists in the scene.")
                
                self.entities.add(entity_id)
                
                if position: self.position[entity_id] = position
                if velocity: self.velocity[entity_id] = velocity
                if old_acceleration: self.old_acceleration[entity_id] = old_acceleration
                if new_acceleration: self.new_acceleration[entity_id] = new_acceleration
                
        def remove_entity(self, entity_id : str):
                self.entities.discard(entity_id)
                
                if entity_id in self.position:
                        del self.position[entity_id]
                if entity_id in self.velocity:
                        del self.velocity[entity_id]
                if entity_id in self.old_acceleration:
                        del self.old_acceleration[entity_id]
                if entity_id in self.acceleration:
                        del self.acceleration[entity_id]

        @abstractmethod
        def step():
                raise NotImplementedError("Scene step method is not implemented yet.")