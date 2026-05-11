from abc import ABC

import unit

class UnitHolder(ABC):
        """
                Container class for managing units by type and id.
                This can be used for various purposes, such as managing game entities, components, or any other units that need to be organized by type and id.
        """
        def __init__(self):
                self.components : dict[str, dict[str, list[unit.Unit]]]= {}
        
        def add_component(self, component : unit.Unit):
                class_name = component.__class__.__name__
                
                id = component.id
                
                if class_name not in self.components:
                        self.components[class_name] = {}
                        
                if id not in self.components[class_name]:
                        self.components[class_name][id] = []
                
                self.components[class_name][id].append(component)   
        
        def get_components(self, component_class : type[unit.Unit], id : str):
                return self.components.get(component_class.__name__, {}).get(id, [])