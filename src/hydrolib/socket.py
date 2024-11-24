import asyncio
import socket
from typing import Any


class Asyncsocket:
    """
    socket.socket的异步版本
    """
    def __init__(self, s: socket.socket | Any = None, event_loop: asyncio.AbstractEventLoop = None):
        if s is None:
            self.sock = socket.socket()
        elif isinstance(s, self.__class__):
            self.sock = s.sock
        else:
            self.sock = s

        self.event_loop = event_loop

    async def write(self, data):
        return await self.event_loop.sock_sendall(
            self.sock, data
        )

    async def recv(self, size: int):
        return await self.event_loop.sock_recv(
            self.sock, size
        )

    async def accept(self):
        return await self.event_loop.sock_accept(self.sock)

    async def connect(self, addr):
        return await self.event_loop.sock_connect(self.sock, addr)

    async def connect_ex(self, addr):
        return self.sock.connect_ex(addr)

    def settimeout(self, timeout=None):
        self.sock.settimeout(timeout)

    def listen(self, backlog):
        self.sock.listen(backlog)

    def detach(self):
        return self.sock.detach()

    def family(self):
        return self.sock.family

    def fileno(self):
        return self.sock.fileno()

    async def get_inheriteable(self):
        return self.sock.get_inheritable()

    def getblocking(self):
        return self.sock.getblocking()

    def getpeername(self):
        return self.sock.getpeername()

    def getsockname(self):
        return self.sock.getsockname()

    def getsockopt(self, level, optname, buflen=None):
        if buflen is None:
            return self.sock.getsockopt(level, optname)
        else:
            return self.sock.getsockopt(level, optname, buflen)

    def gettimeout(self):
        return self.sock.gettimeout()

    def ioctl(self, control, option):
        return self.sock.ioctl(control, option)

    async def bind(self, addr):
        self.sock.bind(addr)

    async def close(self):
        self.sock.close()
