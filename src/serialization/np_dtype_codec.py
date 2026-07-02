from serialization.codec import Codec

import numpy


class NPDtypeCodec(Codec):
    target_type = numpy.void
    marker = "dtype"

    @staticmethod
    def encode_dtype(dtype: numpy.dtype) -> list:
        result = []

        for field in dtype.descr:
            name = field[0]
            subdtype = field[1]

            if isinstance(subdtype, list):
                result.append([name, NPDtypeCodec.encode_dtype(numpy.dtype(subdtype))])
            else:
                result.append([name, str(subdtype)])

        return result

    @staticmethod
    def decode_dtype(descr: list, align=False) -> numpy.dtype:
        result = []

        for name, subdtype in descr:
            if isinstance(subdtype, list):
                result.append((name, NPDtypeCodec.decode_dtype(subdtype)))
            else:
                result.append((name, numpy.dtype(subdtype)))

        return numpy.dtype(result, align=align)

    @staticmethod
    def encode(obj: numpy.void):
        result = {}

        result["dtype"] = NPDtypeCodec.encode_dtype(obj.dtype)

        for name in obj.dtype.names:
            result[name] = obj[name].item()

        return result

    @staticmethod
    def decode(data: dict):
        dtype = NPDtypeCodec.decode_dtype(data[NPDtypeCodec.marker])

        values = tuple(data[name] for name in dtype.names)

        return numpy.array([values], dtype=dtype)[0]
