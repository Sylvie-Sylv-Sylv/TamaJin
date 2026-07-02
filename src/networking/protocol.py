from enum import Enum
from socket import SOCK_STREAM, SOCK_DGRAM


class Protocol(Enum):
    TCP = SOCK_STREAM
    UDP = SOCK_DGRAM
