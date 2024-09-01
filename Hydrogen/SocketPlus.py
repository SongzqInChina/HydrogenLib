import builtins
import datetime
import queue
import socket
import time
import warnings
from typing import (
    Callable
)

from . import StructPlus
from . import ThreadingPlus
from . import TypeFunc
from .Classes.Null import null
from .DataStructures import ThreadSafeCollections


# module end at 8/1/2024
# module start at 8/21/2024  # 完成一个远程代理服务类
# module end at 8/23/2024 # 代理服务类没做完，做完了一个简单的服务器类
# 基于此的BoardcastRoom仍处于开发状态


class _BaseSimpleSocket:
    def __init__(self, s: socket.socket | object | None = None):
        self.read_loop_event = None
        self.write_loop_event = None
        self.read_thread = None
        self.write_thread = None
        if s is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif isinstance(s, self.__class__):
            self.sock = s.sock

        self.lasterror = None
        self._buffer = queue.Queue(256)
        self._write_buffer = queue.Queue(256)

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

    def connect(self, host, port, timeout=None):
        try:
            self.sock.settimeout(timeout)
            self.sock.connect((host, port))
            self.getlasterror()
            self.start_server()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    def bindport(self, port):  # 绑定端口
        try:
            self.sock.bind(('', port))
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    def bind(self, host, port):  # 绑定端口
        try:
            self.sock.bind((host, port))
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    def listen(self, backlog=1):
        try:
            self.sock.listen(backlog)
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    def accept(self):
        conn, addr = self.sock.accept()
        conn_simple = self.__class__()
        conn_simple.set(conn)
        conn_simple.start_server()
        return conn_simple, addr

    def _write(self, data):
        packing_data_bytes = StructPlus.simple_jsonpickle_pack(data)

        try:
            self.sock.sendall(packing_data_bytes)
            self.getlasterror()
            return True
        except socket.error as e:
            self.lasterror = e
            return False

    def _read_loop(self, StopEvent):
        while True:
            if StopEvent.is_set():
                return

            data = self._read()
            if data is not None:
                for item in data:
                    self._buffer.put(item)

    def _read(self):
        every_data = b""
        try:
            while True:
                every_data += self.sock.recv(65535)
                if len(every_data) < 65535:
                    break

        except socket.herror as e:
            self.lasterror = e
            return None

        if every_data == b'':
            return None

        unpacking_datas = StructPlus.simple_jsonpickle_unpacks(every_data)
        return unpacking_datas

    def read(self, timeout=None):
        try:
            data = self._buffer.get(timeout=timeout)
            self._buffer.task_done()
        except queue.Empty:
            return None
        return data

    def write(self, data):
        self._write_buffer.put(data)

    def _write_loop(self, StopEvent):
        while StopEvent.is_set():
            try:
                data = self._write_buffer.get(timeout=0.5)
                self._write(data)
                self._write_buffer.task_done()
            except queue.Empty:
                continue

    def empty(self):
        return self._buffer.empty()

    def start_server(self):
        if self.read_thread is not None and self.write_thread is not None:
            self.read_loop_event = ThreadingPlus.threading.Event()
            self.write_loop_event = ThreadingPlus.threading.Event()
            self.read_thread = ThreadingPlus.start_new_thread(self._read_loop, self.read_loop_event)
            self.write_thread = ThreadingPlus.start_new_thread(self._write_loop, self.write_loop_event)

    def stop_server(self):
        if self.read_thread is not None:
            self.read_loop_event.set()
        if self.write_thread is not None:
            self.write_loop_event.set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


Sockets = socket.socket | _BaseSimpleSocket


class SimpleSocket:
    def __init__(self, s: Sockets | object | None = None):
        if isinstance(s, _BaseSimpleSocket):
            self._socket = s
        else:
            self._socket = _BaseSimpleSocket(s)

    @property
    def sock(self):
        return self._socket.sock

    @property
    def base_socket(self):
        return self._socket

    def set(self, sock, start_server=True):
        self._socket.set(sock, start_server)

    def close(self):
        self._socket.close()

    def getlasterror(self):
        return self._socket.getlasterror()

    def settimeout(self, timeout):
        self._socket.settimeout(timeout)

    def connect(self, host, port, timeout=None):
        return self._socket.connect(host, port, timeout)

    def bindport(self, port):
        return self._socket.bindport(port)

    def bind(self, host, port):
        return self._socket.bind(host, port)

    def listen(self, backlog=1):
        return self._socket.listen(backlog)

    def accept(self):
        conn, addr = self._socket.accept()
        return SimpleSocket(conn), addr

    def read(self, timeout=None):
        return self._socket.read(timeout)

    def write(self, data):
        self._socket.write(data)

    def empty(self):
        return self._socket.empty()

    def start_server(self):
        self._socket.start_server()

    def stop_server(self):
        self._socket.stop_server()

    def self_accept(self):
        self._socket.close()
        self._socket = self._socket.accept()[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def is_tcp(s: SimpleSocket | socket.socket):
    if isinstance(s, SimpleSocket):
        return is_tcp(s.sock)
    else:
        return s.type == socket.SOCK_STREAM


def is_udp(s: SimpleSocket | socket.socket):
    if isinstance(s, SimpleSocket):
        return is_udp(s.sock)
    else:
        return s.type == socket.SOCK_DGRAM


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

    def __init__(self, sp_socket: SimpleSocket):
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
        self.socket = RemotePost(SimpleSocket())
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
        self.sock = SimpleSocket()
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
        self.sock = SimpleSocket()
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


class Server:
    def __init__(self):
        self.sock = SimpleSocket()
        self.sock.start_server()  # 控制socket启动监听线程

        self.max_connects = 10
        self.max_wait_queue_length = 10

        self.requests = ThreadSafeCollections.SafeList()
        self.thread = None
        self.stop_event = ThreadingPlus.threading.Event()
        self.connects = []
        self.events = ThreadSafeCollections.SafeList()
        self.events.list *= 10

    def start_server(self):
        def server():
            while not self.stop_event.is_set():
                request = self.sock.read()
                self.requests.append(request)

        self.thread = ThreadingPlus.start_daemon_thread(server)

    def bindport(self, port):
        self.sock.bindport(port)

    def stop_server(self):
        if self.thread is not None and self.thread.alive:
            self.stop_event.set()
            self.thread.join()

    def close(self):
        self.stop_server()
        self.sock.close()

    def listen(self):
        self.sock.listen(self.max_wait_queue_length)

    def accept(self):
        conn, addr = self.sock.accept()
        tid = len(self.connects)
        self.connects.append(conn)
        self.events.append(ThreadingPlus.threading.Event())
        ThreadingPlus.start_daemon_thread(self._process_loop, tid)

    def get_requests(self):
        x = self.requests.copy()
        self.requests.list = []
        return x

    def get_request(self):
        return self.requests.pop(0)

    def _process_loop(self, tid: int):
        while not self.events[tid].is_set():
            package = self.connects[tid].read()
            if package is not None:
                self.requests.append(package)
