import asyncio
from asyncio.queues import Queue

from ... import hystruct
from ...socket import Asyncsocket


class ItemTransfer:
    def __init__(self, sock: Asyncsocket, buffer_size: int = 0):
        self.sock = sock
        self.coder = None
        self._buffer = Queue(buffer_size)
        self._stop_event = asyncio.Event()

    def set_coder(self, coder):
        self.coder = coder

    async def __readall(self):
        data = ''
        while True:
            temp = await self.sock.recv(65536)
            if not temp:
                break
            data += temp
        return data

    async def __read_loop(self):
        while not self._stop_event.is_set():
            data = await self.__readall()
            origin_data = hystruct.Serializers.unpack(data)
            await self._buffer.put(origin_data)

    async def send(self, data):
        await self.sock.sendall(hystruct.Serializers.pack(data, self.coder))

    async def read(self, size=1):
        for i in range(size):
            yield await self._buffer.get()
