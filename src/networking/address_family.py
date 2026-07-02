from enum import Enum
from socket import AF_INET, AF_INET6


class AddressFamily(Enum):
    IPv4 = AF_INET
    IPv6 = AF_INET6
