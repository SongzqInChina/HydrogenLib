from io import *


class SocketIO(IOBase):
    def __init__(self):
        self.data = b''
        self.pos = 0

    def send(self, data):
        self.data += data

    def recv(self, size):
        self.pos += size
        return self.data[self.pos - size:self.pos]
