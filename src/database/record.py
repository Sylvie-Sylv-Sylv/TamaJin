from serialization.obj_codec import ObjTypeRegistry

class Record:
    def __init__(self, name: str = None):
        self.name = name
        
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ObjTypeRegistry.register(cls)