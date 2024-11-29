# import asyncio
# from asyncio import Event, Lock
#
# from ._packages import *
# from .errors import *
# from ..socket import Asyncsocket
# from ..socket_structure.SocketGroup import AsyncSocketGroup, SocketConnect
#
# TODO: Finish this module.
# class SocketBroadcastRoomServer:
#     def __init__(self, port):
#         self.port = port
#
#         self.sock = Asyncsocket()
#         self.group = AsyncSocketGroup(self.sock)
#
#         self.members = {}  # type: dict[str, SocketConnect]
#         self.Broadcast_buffer = asyncio.Queue()
#
#         self._request_processer_event = Event()
#         self._info_processer_event = Event()
#
#         self.member_lock = Lock()
#
#     async def Broadcast(self, data):
#         await self.Broadcast_buffer.put(data)
#
#     async def close(self):
#         await self.group.close_all()
#         await self.sock.close()
#
#     async def _process_one_request(self, conn: SocketConnect):
#         """
#         处理一个连接请求
#         """
#         v = await conn.conn.read(5)
#         if v is None:
#             return False
#         if not isinstance(v, Register):
#             return False
#
#         name = v.get()
#         async with self.member_lock:
#             if name in self.members:
#                 await conn.conn.write(Deny("Name already exists"))
#                 await self.group.close_delete(conn)
#                 return False
#             self.members[name] = conn
#             await conn.conn.write(OK())
#             return True
#
#     async def _processing_request(self):
#         """
#         读取多个连接请求，并依次传递给self._process_one_requset方法
#         """
#         while not self._request_processer_event.is_set():
#             new_connects = await self.group.accept_all()
#             if len(new_connects) == 0:
#                 await asyncio.sleep(0.1)
#                 continue
#             tasks = [self._process_one_request(conn) for conn in new_connects]
#             await asyncio.gather(*tasks)
#
#     async def _processing_info(self):
#         while not self._info_processer_event.is_set():
#             async with self.member_lock:
#                 tasks = []
#                 for name in self.members:
#                     conn = self.members[name]
#                     Broadcast_info = await conn.conn.read(0.5)
#
#                     if isinstance(Broadcast_info, Broadcast):
#                         data = Broadcast_info.get()
#                         tasks.append(
#                             asyncio.create_task(self.Broadcast_buffer.put(Data(data))))
#
#                     if isinstance(Broadcast_info, Unregister):
#                         tasks.append(
#                             asyncio.create_task(self.group.close_delete(conn)))
#                         self.members.pop(name)
#
#                 await asyncio.gather(*tasks)
#
#     async def _send_Broadcast(self):
#         """
#         广播协程
#         """
#         while not self._info_processer_event.is_set():
#             data = await self.Broadcast_buffer.get()
#             tasks = [member.conn.write(data) for member in self.members.values()]
#             await asyncio.gather(*tasks)
#             self.Broadcast_buffer.task_done()
#
#
# class SocketBroadcastRoomClient:
#     def __init__(self):
#         self.sock = Asyncsocket()
#         self.name = None
#         self._connected = False
#
#     def setname(self, name):
#         self.name = name
#
#     @property
#     def connected(self):
#         return self._connected
#
#     async def connect(self, host, port, timeout=None):
#         if self.name is None:
#             raise ClientNameError("You should set name before connect")
#         await self.sock.connect(host)
#         await self.sock.write(Register(self.name))
#
#         res = await self.sock(timeout)
#         if res is None:
#             raise ClientTimeoutError("Read result timeout")
#         if not isinstance(res, OK):
#             raise ClientError(f"Connect failed, reason={str(res)}")
#         self._connected = True
#
#     async def deconnect(self):
#         await self.sock.write(Unregister())
#         await self.sock.close()
#         self._connected = False
#
#     async def Broadcast(self, data):
#         await self.sock.write(Broadcast(data))
