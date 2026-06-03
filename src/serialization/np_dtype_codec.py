import numpy

class NPDtypeCodec:
        def encode(self, obj : numpy.void):
                result = {}
                
                for name in obj.dtype.names:
                        result[name] = obj[name]
                
                return result
        
        def decode(self, data : dict, component_type : type):
                dtype = component_type.schema
                return numpy.array(tuple(data[name] for name in dtype.names), dtype=dtype)