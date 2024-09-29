from ._packages import *
from ..Class.MemberManager import Manager
from ..CoroPlus import new_event_loop
from ..SocketStructure import AsyncMultiSocket


class BoardcastServer:
    def __init__(self, port):
        self.port = port
        self.sock = AsyncMultiSocket()
        self.manager = Manager()
        self.db = {}
        self.loop = new_event_loop()

        self.sock.create("main")
        self.sock.listen("main", 5)
        self.sock.bindport("main", self.port)

    async def _processing_loop(self):
        while True:
            req = await self.sock.read("main")  # read from main socket
            if not isinstance(req, Join | Login):
                await self.sock.write("main", "Invalid request")
