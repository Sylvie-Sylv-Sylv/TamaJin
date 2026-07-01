from encodings.base64_codec import Codec

from serialization.codecs import Codecs

import serialization.np_dtype_codec


class ObjTypeRegistry:
    types = {}

    # Decorator for registering
    @classmethod
    def register(cls, obj_type: type):
        cls.types[obj_type.__name__] = obj_type
        return obj_type


class ObjCodec(Codec):
    target_type = object
    marker = "__class__"

    def __init__(self):
        pass

    @classmethod
    def serialize(cls, obj: object) -> dict:
        if (
            isinstance(obj, (str, int, float, bool))
            or obj is None
            or obj is True
            or obj is False
        ):
            return obj

        if isinstance(obj, list):
            return [ObjCodec.serialize(x) for x in obj]

        if isinstance(obj, dict):
            return {k: ObjCodec.serialize(v) for k, v in obj.items()}

        for codec in Codecs.codecs.values():
            if isinstance(obj, codec.target_type):
                return codec.encode(obj)

        if hasattr(obj, "__dict__"):
            if obj.__class__.__name__ not in ObjTypeRegistry.types:
                raise TypeError(
                    f"Cannot serialize {type(obj)}: class not registered in ObjTypeRegistry. This error is a safety net for safe decoding."
                )

            return {
                cls.marker: obj.__class__.__name__,
                **{k: ObjCodec.serialize(v) for k, v in obj.__dict__.items()},
            }

        raise TypeError(f"Cannot serialize {type(obj)}")

    @staticmethod
    def encode(obj: object) -> dict:
        data = ObjCodec.serialize(obj)

        return data

    @staticmethod
    def decode(data):
        if isinstance(data, (str, int, float, bool)) or data is None:
            return data

        if isinstance(data, list):
            return [ObjCodec.decode(x) for x in data]

        if isinstance(data, dict):
            # Custom codec objects
            for codec in Codecs.codecs.values():
                if codec.marker in data:
                    return codec.decode(data)

            # Registered class objects
            if ObjCodec.marker in data:
                class_name = data[ObjCodec.marker]

                if class_name not in ObjTypeRegistry.types:
                    raise TypeError(f"Cannot decode unknown class {class_name}")

                obj_type = ObjTypeRegistry.types[class_name]

                obj = obj_type.__new__(obj_type)

                for k, v in data.items():
                    if k == ObjCodec.marker:
                        continue

                    setattr(obj, k, ObjCodec.decode(v))

                return obj

            # Normal dictionary
            return {k: ObjCodec.decode(v) for k, v in data.items()}

        raise TypeError(f"Cannot decode {type(data)}")
