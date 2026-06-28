from serialization.json_codec import JsonCodec

print(JsonCodec.decode(JsonCodec.encode({'a': [1, {'b': 2}]})))