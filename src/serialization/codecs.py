from typings import TYPE_CHECKING

if TYPE_CHECKING:
    from codecs import Codec


class Codecs:
    codecs = {}
    
    def register(cls, codec: type[Codec]):
        cls.codecs[codec.target_type] = codec