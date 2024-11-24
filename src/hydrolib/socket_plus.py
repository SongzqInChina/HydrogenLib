import socket
from typing import Any
from . import struct_plus

from .signal import Signal

raise ImportError("You shouldn't import this module because it's not finished.")
#
#
# class SckItemCommunication:
#     def __init__(self, s: socket.socket | Any = None):
#         self.sock = s
#         self.encoder = Signal(struct_plus.jsonpickle_pack)
#         self.decoder = Signal(struct_plus.jsonpickle_unpack)
#
#     def send(self, data):
#         data = self.encoder(data)
#         return self.sock.sendall(data)
#
#     def read(self, timeout=None):
#         pass
