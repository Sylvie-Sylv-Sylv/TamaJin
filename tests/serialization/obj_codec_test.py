import numpy

from serialization.codecs import Codecs
from serialization.obj_codec import ObjCodec, ObjTypeRegistry
from gameplay.physics.position import Position

@ObjTypeRegistry.register
class B:
    def __init__(self, c: numpy.void):
        self.c = c

@ObjTypeRegistry.register
class A:
    def __init__(self, b: B):
        self.b = b

encoded = ObjCodec.encode(A(B(numpy.array([(1, 2)], dtype = Position.schema)[0])))
decoded = ObjCodec.decode(encoded)

print(encoded)
print(decoded.b.c)
