import i_unit

class UnitHolder():
        """
                Container class for managing units by type and id.
                This can be used for various purposes, such as managing game entities, components, or any other units that need to be organized by type and id.
        """
        def __init__(self):
                self.units : dict[str, dict[str, list[i_unit.Unit]]]= {}
        
        def add_unit(self, unit : i_unit.Unit):
                class_name = unit.__class__.__name__
                
                id = unit.id
                
                if class_name not in self.units:
                        self.units[class_name] = {}
                        
                if id not in self.units[class_name]:
                        self.units[class_name][id] = []
                        
                unit.unit_holder = self
                
                self.units[class_name][id].append(unit)   
        
        def fetch_units(self, unit_class : type[i_unit.Unit], id : str):
                return self.units.get(unit_class.__name__, {}).get(id, [])
        
        def remove_unit(self, unit_class : type[i_unit.Unit], id : str):
                if unit_class.__name__ in self.units and id in self.units[unit_class.__name__]:
                        del self.units[unit_class.__name__][id]