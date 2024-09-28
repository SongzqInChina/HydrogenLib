import asyncio
import socket

from . import CoroPlus
from . import StructPlus


# module end at 8/1/2024
# module start at 8/21/2024  # 完成一个远程代理服务类
# module end at 8/23/2024 # 代理服务类没做完，做完了一个简单的服务器类
# 基于此的BoardcastRoom仍处于开发状态

class AsyncSocket:
    def __init__(self, s: socket.socket | object | None = None):
        self.read_loop_event = asyncio.Event()
        self.write_loop_event = asyncio.Event()
        self.read_coro = None
        self.write_coro = None
        if s is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif isinstance(s, self.__class__):
            self.sock = s.sock

        self.lasterror = None
        self._buffer = asyncio.Queue(256)
        self._write_buffer = asyncio.Queue(256)

    def set(self, sock, start_server=True):
        self.sock.close()
        self.sock = sock  # type: socket.socket
        if start_server:
            self.start_server()

    def close(self):
        self.stop_server()
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError as e:
            self.lasterror = e
        self.sock.close()

    def getlasterror(self):
        e = self.lasterror
        self.lasterror = None
        return e

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def empty(self):
        return self._buffer.empty()

    async def connect(self, host, port, timeout=None):
        try:
            self.sock.settimeout(timeout)
            await asyncio.get_event_loop().sock_connect(self.sock, (host, port))
            self.getlasterror()
            self.start_server()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    async def bindport(self, port):  # 绑定端口
        try:
            self.sock.bind(('', port))
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    async def bind(self, host, port):  # 绑定端口
        try:
            self.sock.bind((host, port))
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    async def listen(self, backlog=1):
        try:
            self.sock.listen(backlog)
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    async def accept(self):
        conn, addr = await asyncio.get_event_loop().sock_accept(self.sock)
        conn_simple = self.__class__()
        conn_simple.set(conn)
        conn_simple.start_server()
        return conn_simple, addr

    async def _write(self, data):
        packing_data_bytes = StructPlus.simple_jsonpickle_pack(data)

        try:
            await asyncio.get_event_loop().sock_sendall(self.sock, packing_data_bytes)
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    async def _read_loop(self):
        loop = asyncio.get_event_loop()
        while not self.read_loop_event.is_set():
            try:
                length_data = await loop.sock_recv(self.sock, 8)
                length = StructPlus.ostruct.unpack(int, length_data)
                data = await loop.sock_recv(self.sock, length)
                self._buffer.put_nowait(data)
            except Exception as e:
                self.lasterror = e
                break

    async def _write_loop(self):
        while not self.write_loop_event.is_set():
            data = await self._write_buffer.get()
            await self._write(data)
            self._write_buffer.task_done()

    async def read(self, timeout=None):
        try:
            data = await asyncio.wait_for(self._buffer.get(), timeout=timeout)
            self._buffer.task_done()
        except asyncio.TimeoutError:
            return None
        return data

    def write(self, data):
        self._write_buffer.put_nowait(data)

    def start_server(self):
        self.read_coro = asyncio.create_task(self._read_loop())
        self.write_coro = asyncio.create_task(self._write_loop())

    def stop_server(self):
        self.read_loop_event.set()
        self.write_loop_event.set()
        if self.read_coro is not None:
            self.read_coro.cancel()
        if self.write_coro is not None:
            self.write_coro.cancel()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


Sockets = socket.socket | AsyncSocket


class SyncSocket:
    def __init__(self, s: Sockets | object | None = None):
        if isinstance(s, AsyncSocket):
            self._socket = s
        else:
            self._socket = AsyncSocket(s)
        self.loop = CoroPlus.new_event_loop()

    def _run(self, func_name, *args, **kwargs):
        return CoroPlus.run_in_existing_loop(
            getattr(self._socket, func_name)(*args, **kwargs),
            self.loop
        )

    @property
    def sock(self):
        return self._socket.sock

    def getlasterror(self):
        return self._run('getlasterror')

    def set(self, sock, start_server=True):
        self._socket.set(sock, start_server)

    def settimeout(self, timeout):
        self._run('settimeout', timeout)

    def empty(self):
        return self._run('empty')

    def bindport(self, port):
        return self._run('bindport', port)

    def bind(self, host, port):
        return self._run('bind', host, port)

    def listen(self, backlog=1):
        return self._run('listen', backlog)

    def accept(self):
        return self._run('accept')

    def connect(self, host, port, timeout=None):
        return self._run('connect', host, port, timeout)

    def read(self, timeout=None):
        return self._run('read', timeout)

    def write(self, data):
        return self._run('write', data)

    def start_server(self):
        self._socket.start_server()

    def self_accept(self):
        origin_socket = self._socket
        self._socket = self.accept()
        origin_socket.close()
        return self._socket

    def close(self):
        self._socket.close()
        self.loop.close()


def is_tcp(s: SyncSocket | socket.socket):
    if isinstance(s, SyncSocket):
        return is_tcp(s.sock)
    else:
        return s.type == socket.SOCK_STREAM


def is_udp(s: SyncSocket | socket.socket):
    if isinstance(s, SyncSocket):
        return is_udp(s.sock)
    else:
        return s.type == socket.SOCK_DGRAM
