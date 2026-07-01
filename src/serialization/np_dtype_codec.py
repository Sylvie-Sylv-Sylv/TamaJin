from serialization.codec import Codec

import numpy

class NPDtypeCodec(Codec):
    target_type = numpy.void
    marker = 'dtype'
    
    @staticmethod
    def encode(obj : numpy.void):
        result = {}
        
        result['dtype'] = obj.dtype.descr
        
        for name in obj.dtype.names:
            result[name] = obj[name].item()
        
        return result
    
    @staticmethod
    def decode(data: dict):
        dtype = numpy.dtype(data[NPDtypeCodec.marker])

        values = tuple(
            data[name]
            for name in dtype.names
        )

        return numpy.array(
            [values],
            dtype=dtype
        )[0]