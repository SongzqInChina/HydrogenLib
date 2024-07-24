import builtins
import hashlib
import queue
import re
import socket
import time
import warnings
from typing import (
    Callable
)

import ping3

from . import typefunc
from . import zstruct
from . import zthread as libthreading


# module end


def _ipa():
    """
    返回一个A类IP地址的迭代器
    :return:
    """
    i1 = 10
    for i2 in range(256):
        for i3 in range(256):
            for i4 in range(256):
                yield f"{i1}.{i2}.{i3}.{i4}"


def _ipb():
    """
    返回一个B类IP地址的迭代器
    :return:
    """
    i1 = 172
    for i2 in range(16, 32):
        for i3 in range(256):
            for i4 in range(256):
                yield f"{i1}.{i2}.{i3}.{i4}"


def _ipc():
    """
    返回一个C类IP地址的迭代器
    :return:
    """
    i1 = 192
    i2 = 168
    for i3 in range(256):
        for i4 in range(256):
            yield f"{i1}.{i2}.{i3}.{i4}"


def _ipd():
    """
    返回一个D类IP地址的迭代器
    :return:
    """
    for i1 in range(110, 132):
        for i2 in range(256):
            for i3 in range(256):
                for i4 in range(256):
                    yield f"{i1}.{i2}.{i3}.{i4}"


def _ipe():
    """
    返回一个E类IP地址的迭代器
    :return:
    """
    i1 = 127
    for i2 in range(256):
        for i3 in range(256):
            for i4 in range(256):
                yield f"{i1}.{i2}.{i3}.{i4}"


def _ipf():
    """
    返回一个F类IP地址的迭代器
    :return:
    """
    i1 = 169
    i2 = 254
    for i3 in range(256):
        for i4 in range(256):
            yield f"{i1}.{i2}.{i3}.{i4}"


def _getIP(IPClass: str):
    IPClass = IPClass.upper()[0]
    if IPClass == "A":
        return _ipa()
    elif IPClass == "B":
        return _ipb()
    elif IPClass == "C":
        return _ipc()
    elif IPClass == "D":
        return _ipd()
    elif IPClass == "E":
        return _ipe()
    elif IPClass == "F":
        return _ipf()
    else:
        return None


def getIP(IPClass: str):
    """
    IP范围：\n
    - A: 10.0.0.0-10.255.255.255\n
    - B: 172.16.0.0-172.31.255.255\n
    - C: 192.168.0.0-192.168.255.255\n
    - D: 110.0.0.0-127.255.255.255\n
    - E: 127.0.0.0-127.255.255.255\n
    - F: 169.254.0.0-169.254.255.255\n
    :param IPClass: A, B, C, D, E, F
    :return:
    """
    for i in _getIP(IPClass):
        yield i


def ping(name, timeout=1):
    """
    检查网络连通性
    :param name:
    :param timeout:
    :return:
    """
    return ping3.ping(name, timeout=timeout)


def can_ping(name, timeout=1):
    """
    是否能ping通
    :param name:
    :param timeout:
    :return:
    """
    return bool(ping(name, timeout))


def getIPseq(ip1a, ip1b, ip2a, ip2b, ip3a, ip3b, ip4a, ip4b):
    for ip1 in range(ip1a, ip1b):
        for ip2 in range(ip2a, ip2b):
            for ip3 in range(ip3a, ip3b):
                for ip4 in range(ip4a, ip4b):
                    yield f"{ip1}.{ip2}.{ip3}.{ip4}"


def _getIPv6seq(ip_ranges):
    def parse_hex_range(hex_range: str):
        match = re.match(r'^0x([0-9a-fA-F]+)-0x([0-9a-fA-F]+)$', hex_range)
        if match:
            return int(match.group(1), 16), int(match.group(2), 16)
        else:
            raise ValueError(f"Invalid hexadecimal range: {hex_range}")

    parsed_ranges = [parse_hex_range(hr) for hr in ip_ranges]

    for ip1 in range(parsed_ranges[0][0], parsed_ranges[0][1]):
        for ip2 in range(parsed_ranges[1][0], parsed_ranges[1][1]):
            for ip3 in range(parsed_ranges[2][0], parsed_ranges[2][1]):
                for ip4 in range(parsed_ranges[3][0], parsed_ranges[3][1]):
                    for ip5 in range(parsed_ranges[4][0], parsed_ranges[4][1]):
                        for ip6 in range(parsed_ranges[5][0], parsed_ranges[5][1]):
                            for ip7 in range(parsed_ranges[6][0], parsed_ranges[6][1]):
                                for ip8 in range(parsed_ranges[7][0], parsed_ranges[7][1]):
                                    hex_ip1 = format(ip1, '04x')
                                    hex_ip2 = format(ip2, '04x')
                                    hex_ip3 = format(ip3, '04x')
                                    hex_ip4 = format(ip4, '04x')
                                    hex_ip5 = format(ip5, '04x')
                                    hex_ip6 = format(ip6, '04x')
                                    hex_ip7 = format(ip7, '04x')
                                    hex_ip8 = format(ip8, '04x')

                                    yield \
                                        f"{hex_ip1}:{hex_ip2}:{hex_ip3}:{hex_ip4}:{hex_ip5}:{hex_ip6}:{hex_ip7}:{hex_ip8}"


def getIPv6seq(
        ip1='0x0-0xffff',
        ip2='0x0-0xffff',
        ip3='0x0-0xffff',
        ip4='0x0-0xffff',
        ip5='0x0-0xffff',
        ip6='0x0-0xffff',
        ip7='0x0-0xffff',
        ip8='0x0-0xffff'
):
    return _getIPv6seq([ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8])


def getIPv6seqi(
        ip1='0-65536',
        ip2='0-65536',
        ip3='0-65536',
        ip4='0-65536',
        ip5='0-65536',
        ip6='0-65536',
        ip7='0-65536',
        ip8='0-65536'
):
    # Convert integer ranges to hexadecimal format for compatibility with _getIPv6seq function
    hex_ip_ranges = [f"0x{ip1[0]:04x}-0x{ip1[1]:04x}",
                     f"0x{ip2[0]:04x}-0x{ip2[1]:04x}",
                     f"0x{ip3[0]:04x}-0x{ip3[1]:04x}",
                     f"0x{ip4[0]:04x}-0x{ip4[1]:04x}",
                     f"0x{ip5[0]:04x}-0x{ip5[1]:04x}",
                     f"0x{ip6[0]:04x}-0x{ip6[1]:04x}",
                     f"0x{ip7[0]:04x}-0x{ip7[1]:04x}",
                     f"0x{ip8[0]:04x}-0x{ip8[1]:04x}"]

    # Validate the input ranges
    for range_str in hex_ip_ranges:
        start, end = range_str.split('-')
        if int(start, 16) < 0 or int(end, 16) > 0xffff:
            raise ValueError(f"Invalid IPv6 sequence integer range: {range_str}")

    return _getIPv6seq(hex_ip_ranges)


def IP4to6(ip4):
    ipv4_bytes = ip4.split('.')

    # 将每个字节转换为十六进制并补足到四位（例如 '0' + '123' -> '0123'）
    ipv4_hex = [hex(int(byte))[2:].zfill(2) for byte in ipv4_bytes]

    # IPv4地址内嵌到IPv6地址的格式为 ::ffff:0a0b:0c0d，其中0a0b:0c0d是IPv4地址的十六进制形式
    ipv6_prefix = "ffff:"
    ipv6_mapped = ipv6_prefix + ":".join(ipv4_hex)

    # 前面添加 "::" 表示高位部分全为0
    full_ipv6_address = "::" + ipv6_mapped

    return full_ipv6_address


def toip(url):
    try:
        ip = socket.gethostbyname(url)
    except socket.gaierror:
        ip = None
    return ip


def toname(ip):
    # 尝试将IP地址解析为域名
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        # 如果出现无法反向解析IP地址的情况，返回错误信息
        return None


def is_simple_request(header):
    if not isinstance(header, dict):
        return False
    for k in ["type", "header", "hash"]:
        if k not in header:
            return False
    if header["hash"] != hashlib.sha256(header["header"].encode()).hexdigest():
        return False
    return True


def create_simple_request(_type="Get-Request", header=None):
    request = {
        "type": _type,
        "header": header,
        "hash": hashlib.sha256(header.encode()).hexdigest()
    }
    return request


def create_simple_answer(_type="Get-Answer", header=..., _answer=...):
    answer = {
        "type": _type,
        "header": header,
        "data": _answer,
        "hash": hashlib.sha256(header.encode()).hexdigest()
    }
    return answer


class SimpleSocket:
    def __init__(self, s: socket.socket | object | None = None):
        self.lock_event = None
        self.thread = None
        if s is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif isinstance(s, self.__class__):
            self.sock = s.sock

        self.lasterror = None
        self._buffer = queue.Queue(256)

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
        return conn_simple, addr

    def write(self, data):
        packing_data_bytes = zstruct.simple_jsonpickle_pack(data)

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
                print("Return")
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

        unpacking_datas = zstruct.simple_jsonpickle_unpacks(every_data)
        return unpacking_datas

    def read(self, timeout=None):
        try:
            data = self._buffer.get(timeout=timeout)
        except queue.Empty:
            return None
        return data

    def start_server(self):
        self.lock_event = libthreading.threading.Event()
        self.thread = libthreading.start_new_thread(self._read_loop, self.lock_event)

    def stop_server(self):
        if self.thread:
            self.lock_event.set()

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

        def __iter__(self):
            return self.data.keys()

    def __init__(self, sp_socket: SimpleSocket):
        self.socket = sp_socket
        # 优先度
        self.priority = None
        # 回合
        self.round = 0

    def server(self, port):
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

    def can_send(self):
        return self.round % 2 == self.priority

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
        self.socket.server(port)

    def link(self, func):
        if not typefunc.func.is_callable(func):
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
        if typefunc.func.is_callable(func):
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
        self.lock_event = libthreading.threading.Event()
        self.thread = libthreading.start_new_thread(self._post_loop, self.lock_event)

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


class MultiSocket(SimpleSocket):
    def __init__(self, *args, **kwargs):
        super(SimpleSocket, self).__init__(*args, **kwargs)
        self.members = []

        self.operates = queue.Queue()
        self.threads = []

        self.request_template = {
            "data": None
        }

    def _accept(self):
        conn, addr = self.accept()
        self.members.append((conn, addr))

    def _socket_listen(self, sock: SimpleSocket):  # 监听一个socket
        def _listen_thread():
            while True:
                try:
                    operate = self.read()
                    if operate.keys() != self.request_template.keys():
                        continue
                    operate['source'] = sock.sock.getpeername()
                    self.operates.put()
                except queue.Empty:
                    pass

