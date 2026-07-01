from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from serialization.codec import Codec


class Codecs:
    codecs = {}
    
    @classmethod
    def register(cls, codec: type[Codec]):
        cls.codecs[codec.target_type] = codec