import asyncio
import builtins
import datetime
import queue
import socket
import time
import warnings
from typing import Callable

from . import TypeFunc, ThreadingPlus
from .Class.Base import null
from .Class.MultiSet import MultiSet
from .CoroPlus import new_event_loop, run_in_existing_loop
from .SocketPlus import SyncSocket, AsyncSocket


class AsyncMultiSocket:
    async def put_in(self, data, name):
        await self.datas[name].put(data)
        await self.data_index.put(name)

    async def _read_loop(self):

        while not self.event.is_set():
            tasks = []
            for name, sock in self.socks.items():
                if not sock.empty():
                    if name not in self.datas:
                        self.datas[name] = asyncio.Queue()
                    while not sock.empty():
                        task = asyncio.create_task(self._process_data(sock, name))
                        tasks.append(task)
            await asyncio.gather(*tasks)

    def __init__(self, max_concurrency=16):
        self.data_index = asyncio.Queue()
        self.data_vis = MultiSet()
        self.datas = {}  # type: dict[str, asyncio.Queue]
        self.socks = {}  # type: dict[str, AsyncSocket]
        self.loop = new_event_loop()
        self.event = asyncio.Event()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def _process_data(self, sock, name):
        async with self.semaphore:
            while not sock.empty():
                data = await sock.read()
                await self.put_in(data, name)

    async def boardcast(self, data):
        for name, sock in self.socks.items():
            sock.write(data)

    async def _remove_from_index(self, name):
        self.data_vis.add(name)

    async def write(self, name, data):
        self.socks[name].write(data)

    async def read(self, name):
        await self._remove_from_index(name)
        return await self.datas[name].get()

    async def empty(self):
        return self.data_index.empty()

    async def create(self, name):
        self.socks[name] = AsyncSocket()

    async def connect(self, name, host, port, timeout=None):
        return await self.socks[name].connect(host, port, timeout)

    async def accept(self, name):
        return await self.socks[name].accept()

    async def accept_and_add(self, name, nw_name):
        sk = await self.socks[name].accept()
        await self.add(nw_name, sk)

    async def add(self, name, sock):
        if name in self.socks:
            raise Exception("Socket name already exists")
        self.socks[name] = sock

    async def exists(self, name):
        return name in self.socks

    async def remove(self, name):
        if not self.exists(name):
            raise Exception("Socket name not exists")
        await self.socks[name].close()
        del self.socks[name]

    async def get_lasterror(self, name):
        return self.socks[name].getlasterror()

    async def read_one(self):
        name = await self.data_index.get()
        while name in self.data_vis:  # 找到第一个未读取的数据
            self.data_vis.remove(name)
            name = await self.data_index.get()
        return await self.datas[name].get()

    def close(self):
        self.event.set()
        for sock in self.socks.values():
            sock.close()


class SyncMultiSocket:
    def __init__(self):
        self.loop = new_event_loop()

    def _run(self, func_name, *args, **kwargs):
        coro = getattr(self, func_name)(*args, **kwargs)
        return run_in_existing_loop(coro, self.loop)

    def boardcast(self, data):
        self._run('boardcast', data)


class RemotePost:  # RemotePost 使用一问一答形式发送数据
    class _Post:
        def __init__(self, **data):
            self.data = data

        def get(self, key):
            return self.data.get(key)

        def gets(self, keys):
            return [self.data.get(key) for key in keys]

        def cmp(self, key, value):
            return self.data.get(key) == value

        def keys(self):
            return self.data.keys()

        def values(self):
            return self.data.values()

        def has_key(self, key):  # 建议直接使用 key in post 的方式检查
            res = self.data.get(key, null) is not null
            return res

        def __iter__(self):
            return self.data.keys()

    def __init__(self, sp_socket: SyncSocket):
        self.socket = sp_socket
        # 优先度
        self.priority = None
        # 回合
        self.round = 0

    def server_at(self, port):
        self.socket.bindport(port)
        self.socket.listen()
        self.socket.start_server()

    def connect(self, remote_host, remote_port, timeout=None):
        """
        connect a RemotePost Server and return True if success
        :param remote_port: RemotePost Server host
        :param remote_host: RemotePost Server port
        :param timeout: socket.connect(..., ..., timeout=timeout)
        :return: bool
        """
        self.priority = 1  # 客户端优先（自己优先）
        return self.socket.connect(remote_host, remote_port, timeout)

    # 接收连接函数
    def accept(self):
        """
        accept the connect request and reset self
        :return: None
        """
        self.priority = 0  # 客户端优先（对方优先）
        sock = self.socket.accept()[0]
        self.socket.close()
        self.socket = sock

    def send(self, **data):  # 发送报文：字典
        """
        if NOT your round, function throw Exception: "Not your round"
        :param data: dict post
        :return: None
        :raise: Exception
        """
        if self.round % 2 == self.priority:
            self.round += 1
            self.socket.write(data)
        else:
            raise Exception("Not your round")

    def get(self):
        if self.isme():
            return None
        self.round += 1
        x = self.socket.read()
        try:
            while isinstance(x, dict):
                x = self.socket.read(5)
        except queue.Empty:
            return None
        except socket.timeout:
            return None
        return self._Post(**x)

    def isme(self):
        return self.round % 2 == self.priority

    def close(self):
        self.socket.close()


class RemoteCallServer:
    def __init__(self, sp_socket: RemotePost):
        self.lock_event = None
        self.thread = None
        self.socket = sp_socket
        self.functions = {}  # type: dict[str, Callable]

    def server(self, port):
        self.socket.server_at(port)

    def link(self, func):
        if not TypeFunc.Func.is_callable(func):
            raise Exception("Func param must be callable")
        func_name = func.__name__
        if func is builtins.eval or func_name == "eval":
            warnings.warn("Registering 'eval' function is potentially dangerou. Exercise extreme caution!",
                          category=UserWarning)
        self.functions[func_name] = func

    def unlink(self, func):
        type_ = type(func)
        if type_ == str:
            return self.functions.pop(type_)
        if TypeFunc.Func.is_callable(func):
            return self.functions.pop(func.__name__)
        raise Exception("Func param must be str or a func")

    def _post_loop(self, StopEvent):
        while True:
            if StopEvent.is_set():
                return
            post = self.socket.get()
            if post is not None:
                if "fc_name" not in post or "fc_args" not in post or "fc_kwargs" not in post:
                    continue  # error call_request
                fc_name, fc_args, fc_kwargs = post.gets(["fc_name", "fc_args", "fc_kwargs"])
                if fc_name not in self.functions:  # function not found
                    self.socket.send(
                        fc_name=fc_name,
                        time=time.time(),
                        result=("server_error", RuntimeError("Function not found"))
                    )  # send error
                func = self.functions[fc_name]  # get function
                try:
                    result = func(*fc_args, **fc_kwargs)  # call function
                    self.socket.send(fc_name=fc_name, time=time.time(), result=("ok", result))  # send result
                except Exception as e:
                    self.socket.send(fc_name=fc_name, time=time.time(), result=("error", e))  # send error

    def server_start(self):
        self.lock_event = ThreadingPlus.threading.Event()
        self.thread = ThreadingPlus.start_new_thread(self._post_loop, self.lock_event)

    def server_stop(self):
        if self.thread:
            self.lock_event.set()

    def close(self):
        self.server_stop()
        self.socket.close()


class RemoteCallClient:
    def __init__(self, remote_host, remote_port, timeout=None):
        self.socket = RemotePost(SyncSocket())
        try:
            self.socket.connect(remote_host, remote_port, timeout)
        except socket.timeout:
            raise Exception("Connect timeout")

    def _request(self, fc_name, fc_args, fc_kwargs):
        self.socket.send(fc_name=fc_name, fc_args=fc_args, fc_kwargs=fc_kwargs)
        answer = self.socket.get()
        if answer is None:
            raise Exception("No answer")
        result = answer.get("result")
        return dict(
            time=answer.get("time"),
            ok=result[0] == "ok",
            return_value=result[1],
            result=result
        )

    def request(self, fc_name, *fc_args, **fc_kwargs):
        return self._request(fc_name, fc_args, fc_kwargs)

    def close(self):
        self.socket.close()


class HeartbeatPacketClient:
    def __init__(self):
        """
        自动发送心跳包
        """
        self.sock = SyncSocket()
        self.post = RemotePost(self.sock)
        self.timer = None

    def connect(self, lc_port, rc_host, rc_port):
        self.sock.bindport(lc_port)
        res = self.sock.connect(rc_host, rc_port)
        if res is False:
            raise self.sock.getlasterror() from None

    def start(self, time=15):
        def send():
            self.post.send(time=datetime.datetime.now())

        self.timer = ThreadingPlus.threading.Timer(time, send)
        self.timer.daemon = True
        self.timer.start()

    def cancel(self):
        self.timer.cancel()


class HeartbeatPacketServer:
    """
    自动接收并相应心跳包
    """

    def __init__(self):
        self.thread = None
        self.sock = SyncSocket()
        self.post = RemotePost(self.sock)
        self.timer = None
        self.timeout = 5
        self.last_packet = None

    def listen(self):
        self.sock.listen()

    def accept(self):
        self.sock.self_accept()

    def start(self):
        def wrapper():
            while True:
                packet = self.post.get()  # 读取
                # 根据协议，这个包应该是一个_Post字典，且time值是一个datatime类型
                if "time" not in packet:
                    continue
                if not isinstance(packet.get("time"), datetime.datetime | datetime.timedelta):
                    continue
                self.last_packet = packet
                self.post.send(res="OK")  # 响应

        self.thread = ThreadingPlus.start_daemon_thread(wrapper)

    def check(self):
        time = datetime.datetime.now() - self.last_packet.get('time')
        seconds = time.total_seconds()
        if seconds > self.timeout:
            return False
        else:
            return True
