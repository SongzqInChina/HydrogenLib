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
from .CoroPlus import new_event_loop
from .SocketPlus import SyncSocket, AsyncSocket


class AsyncSocketGroup:
    """
    处理一个Socket以及与它相关的连接
    """

    def __init__(self, main_sock: AsyncSocket):
        self.main = main_sock
        self.connects = []

    async def accept(self):
        """
        接受一个连接，返回套接字和地址
        """
        sck, addr = await self.main.accept()
        self.connects.append(sck)
        return sck, addr

    async def accept_all(self):
        """
        接收所有未处理的连接，返回一个整数，表示新连接的数量
        """
        l = len(self.connects)
        while self.main.has_connects():
            sck, addr = await self.main.accept()
            self.connects.append(sck)
        return len(self.connects) - l

    async def length(self):
        return len(self.connects)

    async def get_connect(self, index):
        return self.connects[index]

    async def __aiter__(self):
        for sck in self.connects:
            yield sck


class AsyncMultiSocket:
    """
    多Socket管理器
    """
    def __init__(self, s: AsyncSocket, loop: asyncio.AbstractEventLoop = None):
        self.main = AsyncSocketGroup(s)
        self.loop = new_event_loop() if loop is None else loop
        self.lock = asyncio.Lock()
        self._connects = {}  # type: dict[str, AsyncSocketGroup]

    @property
    def connects(self):
        """
        加锁的Connects属性
        """
        async with self.lock:
            return self._connects

    async def boardcast(self, data):
        """
        广播数据到所有连接
        """
        for name in self._connects:
            group = self._connects[name]
            self.loop.run_until_complete(
                group.main.write(data)
            )

    async def get(self, name):
        """
        尝试获取一个SocketGroup对象，如果找不到名称，返回None
        """
        if name not in self.connects:
            return None
        return self._connects[name]

    async def create(self, name):
        """
        创建一个新的的SocketGroup
        """
        self.connects[name] = AsyncSocketGroup(AsyncSocket())

    async def add(self, name, sck):
        """
        添加一个已有的SocketGroup或Socket对象
        """
        if name in self.connects:
            raise RuntimeError("name already exists")
        if isinstance(sck, AsyncSocket):
            sck = AsyncSocketGroup(sck)
        self.connects[name] = sck

    async def exists(self, name):
        """
        检查name是否存在
        """
        return name in self._connects

    async def sock(self, name):
        """
        安全读取socket
        """
        return self._connects.get(name)

    async def remove(self, name):
        """
        删除一个Socket对象
        """
        if not self.exists(name):
            raise RuntimeError("name not exists")

        sck = self.connects.pop(name)
        return sck


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
