from __future__ import annotations

import socket
import datetime
import struct
import copy

from serialization.json_codec import JsonCodec
from serialization.obj_codec import ObjCodec


class Packet:
    def __init__(self, handler: str, data):
        self.handler = handler
        self.data = data

    def gen_payload(self, encoding="utf-8"):
        data = {"data": copy.deepcopy(self.data)}

        data["timestamp"] = str(datetime.datetime.now())
        data["handler"] = self.handler

        data = JsonCodec.encode(ObjCodec.encode(data))

        return data

    def send(self, sock: socket.socket, encoding="utf-8"):
        data = self.gen_payload(encoding=encoding)

        sock.sendall(struct.pack("!I", len(data)))
        sock.sendall(data)


class TimedPacket(Packet):
    def __init__(self, timestamp: datetime.datetime, handler: str, data):
        self.timestamp = timestamp
        super().__init__(handler, data)

    @staticmethod
    def recv(sock: socket.socket, encoding="utf-8") -> TimedPacket:
        length = struct.unpack("!I", sock.recv(4))[0]
        decoded = ObjCodec.decode(
            JsonCodec.decode(obj=sock.recv(length), encoding=encoding)
        )

        return TimedPacket(
            timestamp=datetime.datetime.strptime(
                decoded["timestamp"], "%Y-%m-%d %H:%M:%S.%f"
            ),
            handler=decoded["handler"],
            data=decoded["data"],
        )
