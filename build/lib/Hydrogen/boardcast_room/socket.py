import queue
import threading
import time

from ..zlibcon import *
from ..znetwork import *
from ..zthread import start_daemon_thread


class SocketInfo:
    def __init__(self, s: SimpleSocket, a):
        self._socket = s
        self._addr = a

    @property
    def socket(self):
        return self._socket

    @property
    def addr(self):
        return self._addr


class BoardcastRoom:
    """

    # 广播室


    - 服务器程序创建一个广播室以后，所有客户端都可以加入广播室
    - 广播室里的操作全部会被日志记录，所有传输数据的行为都会被服务器程序代理
    """

    def __init__(self, room_name, port_func=None, logger=None):
        r"""
        `__init__`方法不需要port参数，程序会自动根据名称计算出一个port值，当然，你也可以控制port_func参数手动更改算法

        """
        self.process_request_thread = None
        self.process_thread = None
        self.room_name = room_name
        self.members = {}  # type: dict[str, SocketInfo]
        self.groups = {}  # type: dict[str, list[SocketInfo]]
        self.operations = queue.Queue()
        self.system_operations = queue.Queue()
        self.threads = []

        self._listen_timeout = 5

        self.watch_dog_thread = None
        self.watch_dog_event = threading.Event()

        self.listen_threads_event = threading.Event()

        self.process_event = threading.Event()

        if port_func is None:
            port_func = lambda x: int.from_bytes(x.encode()) % 32557 + 2048

        self.port = port_func(room_name)

        self.sock = SimpleSocket()

        try:
            self.sock.bindport(self.port)
        except OSError as e:
            raise e

        if logger is None:
            self.logger = logging.getLogger(self.room_name)
        else:
            self.logger = logger  # type: logging.Logger

        self.logger.info(f"Create new room {room_name}")

    def open_room(self):
        self.sock.listen()
        self.watch_dog_thread = start_daemon_thread(self._watch_dog, self.watch_dog_event)
        self.process_thread = start_daemon_thread(self._listen_socket, self.process_event)
        self.process_request_thread = start_daemon_thread(self._process_request, self.process_event)

    def close(self):
        self.watch_dog_event.set()
        self.listen_threads_event.set()

    def _watch_dog(self, event: threading.Event):
        while not event.is_set():
            try:
                client, addr = self.sock.accept()
                data = client.read(4)
                name = data['name']
                group = data['group']

                if name in self.members:
                    self.logger.error(f"{name}({self.members[name].addr}) is already in room {self.room_name}")
                    client.write(Answer(
                        header={
                            'why': BCR_EXIST_NAME
                        },
                        result=False,
                        action="Return"
                    ))
                    continue

                self.members[name] = SocketInfo(client, addr)
                if group not in self.groups:
                    self.groups[group] = []
                self.groups[group].append(SocketInfo(client, addr))
                self.threads.append(start_daemon_thread(self._listen_socket, self.listen_threads_event))

            except OSError as e:
                self.logger.error(e)

    def _listen_socket(self, name, event: threading.Event):
        sock = self.members[name]
        start_time = time.time()
        while not event.is_set():
            request = sock.socket.read(0.5)
            if request is None:
                self.logger.error(f"Error request: ", request)
                continue
            if time.time() - start_time > self._listen_timeout:
                pass  # TODO: close socket




    def _process_request(self, event: threading.Event):
        while not event.is_set():
            request = self.operations.get(timeout=0.5)
            if request is None:
                continue
            if request['type'] == BCR_GROUP:
                group = request['to']
                for member in self.groups[group]:
                    member.socket.write(request)

                self.logger.info(f"Send {request} to {group}")

            elif request['type'] == BCR_PERSON:
                name = request['to']
                self.members[name].socket.write(request)
                self.logger.info(f"Send {request} to {name}")

            elif request['type'] == BCR_ALL:
                for member in self.members.values():
                    member.socket.write(request)

            elif request['type'] == BCR_RANGE:
                for name, member in self.members.items():
                    if name in request['range']:
                        member.socket.write(request)


class Member:
    def __init__(self):
        self.sock = SimpleSocket()
        self.name = None
        self.group = None

    def connect(self, remote_host, remote_port, name, group):
        self.sock.connect(remote_host, remote_port)
        self.sock.write({
            "name": name,
            "group": group
        })
        result = self.sock.read(3)
        if result['Result']:
            self.name = name
            self.group = group
        else:
            raise Exception(result['Because'])

    def boardcast(self, to, message, boardcast_type=BCR_PERSON):
        self.sock.write({
            "to": to,
            "type": boardcast_type,
            "message": message
        })
