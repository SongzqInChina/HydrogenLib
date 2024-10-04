from src.HydrogenLib.SocketPlus import AsyncSocket


class SocketConnect:
    def __init__(self, conn, index):
        self.conn, self.index = conn, index

    def get(self):
        return self.conn, self.index


class AsyncSocketGroup:
    """
    处理一个Socket以及与它相关的连接
    """

    def __init__(self, main_sock: AsyncSocket):
        self.main = main_sock
        self.connects = []  # type: list[SocketConnect]

    async def accept(self):
        """
        接受一个连接，返回一个连接对象，同时添加到连接列表中
        """
        sck, addr = await self.main.accept()
        self.connects.append(sck)
        return SocketConnect(sck, len(self.connects) - 1), addr

    async def accept_all(self) -> list[SocketConnect]:
        """
        接收所有未处理的连接，返回一个整数，表示新连接的数量
        """
        length = await self.length()
        idx = await self.length() - 1
        while self.main.has_connects():
            sck, addr = await self.main.accept()
            idx += 1
            self.connects.append(SocketConnect(
                sck, idx
            ))
        return self.connects[length:]

    async def length(self):
        return len(self.connects)

    async def get_connect(self, index):
        return self.connects[index]

    async def __aiter__(self):
        for sck in self.connects:
            yield sck

    async def close(self, index):
        await self.connects[index].conn.close()

    async def close_delete(self, index):
        if isinstance(index, SocketConnect):
            index = index.index
        await self.connects[index].conn.close()
        del self.connects[index]

    async def close_all(self):
        await self.main.close()
        for sck in self.connects:
            await sck.conn.close()

    def __delitem__(self, key):
        key = key.index if isinstance(key, SocketConnect) else key
        self.connects.pop(key) if not key >= len(self.connects) else None
