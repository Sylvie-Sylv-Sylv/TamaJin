from serialization.json_parser import JsonParser


class JsonCodec:
    @staticmethod
    def str_to_json(obj: str) -> str:
        return '"' + obj.replace("\\", "\\\\").replace('"', '\\"') + '"'

    @staticmethod
    def obj_to_json(obj) -> str:
        if obj is None:
            return "null"
        if obj is True:
            return "true"
        if obj is False:
            return "false"
        if isinstance(obj, (int, float)):
            return str(obj)
        if isinstance(obj, str):
            return JsonCodec.str_to_json(obj)
        if isinstance(obj, list):
            items = []

            for item in obj:
                items.append(JsonCodec.obj_to_json(item))

            return "[" + ",".join(items) + "]"
        if isinstance(obj, dict):
            items = []

            for key, value in obj.items():
                if not isinstance(key, str):
                    raise TypeError("Key of a json dictionary must be a string.")
                items.append(
                    f"{JsonCodec.str_to_json(key)}:{JsonCodec.obj_to_json(value)}"
                )

            return "{" + ",".join(items) + "}"

        raise TypeError(f"Cannot serialize {type(obj)} to json string.")

    @staticmethod
    def json_to_obj(obj: str):
        return JsonParser(obj).parse_value()

    @staticmethod
    def encode(obj, encoding="utf-8") -> bytes:
        return JsonCodec.obj_to_json(obj).encode(encoding=encoding)

    @staticmethod
    def decode(obj: bytes, encoding="utf-8"):
        return JsonCodec.json_to_obj(obj.decode(encoding))
