import numpy

class NPDtypeCodec:
    @staticmethod
    def encode(obj : numpy.void):
        result = {}
        
        for name in obj.dtype.names:
            result[name] = obj[name]
        
        result['']
        
        return result
    
    @staticmethod
    def decode(data : dict, component_type : type):
        dtype = component_type.schema
        return numpy.array(tuple(data[name] for name in dtype.names), dtype=dtype)