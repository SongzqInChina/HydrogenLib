import socket
from typing import Any

from . import StructPlus
from .Signal import Signal


class SckItemCommunication:
    def __init__(self, s: socket.socket | Any = None):
        self.sock = s
        self.encoder = Signal(StructPlus.jsonpickle_pack)
        self.decoder = Signal(StructPlus.jsonpickle_unpack)

    def send(self, data):
        data = self.encoder(data)
        return self.sock.sendall(data)

    def read(self, timeout=None):

