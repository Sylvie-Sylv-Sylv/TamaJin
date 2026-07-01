from encodings.base64_codec import Codec

from serialization.codecs import Codecs


class ObjTypeRegistry:
    types = {}
    
    @classmethod
    def register(cls, registered_type):
        cls.types[registered_type.__name__] = registered_type
        return registered_type

class ObjCodec(Codec):
    target_type = object
    
    def __init__(self):
        pass
    
    @staticmethod
    def serialize(obj: object) -> dict:
        if isinstance(obj, (str, int, float, bool)) or obj is None or obj is True or obj is False:
            return obj

        if isinstance(obj, list):
            return [ObjCodec.serialize(x) for x in obj]

        if isinstance(obj, dict):
            return {k: ObjCodec.serialize(v) for k, v in obj.items()}

        if hasattr(obj, "__dict__"):
            return {
                "__class__": obj.__class__.__name__,
                **{k: ObjCodec.serialize(v) for k, v in obj.__dict__.items()}
            }
            
        for codec in Codecs.codecs.values():
            if isinstance(obj, codec.target_type):
                return codec.encode(obj)

        raise TypeError(f"Cannot serialize {type(obj)}")
    
    def encode(self, obj: object) -> dict:
        data = {}
        
        obj_type = type(obj).__name__
        
        if obj_type not in ObjTypeRegistry.types:
            raise ValueError(f'Type {obj_type} is not registered.')
        
        data['type'] = obj_type
        
        data['data'] = ObjCodec.serialize(obj.__dict__)
        
        return data

    def decode(self, data: dict) -> object:
        pass