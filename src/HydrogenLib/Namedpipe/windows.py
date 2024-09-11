# Namedpipe for windows
from queue import Queue
from threading import Event

import jsonpickle as json
import win32file
import win32pipe

from ..ThreadingPlus import start_daemon_thread


# module end
# module start at Aug 31st 2024 20:31
# module not end
# TODO: 完成对命名管道的多线程重构

class _Reader:

    def format_name(self):
        return fr"\\.\pipe\{self.name}"

    def __init__(self, name):
        self.name = name
        self._queue = Queue()
        self._event = Event()
        self.handle = win32pipe.CreateNamedPipe(
            self.format_name(),
            win32pipe.PIPE_ACCESS_INBOUND,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65535, 65535,
            0, None
        )
        self._connect()
        self.thread = start_daemon_thread(self._read_thread)

    def _connect(self):
        win32pipe.ConnectNamedPipe(self.handle, None)

    def _read(self):
        self._connect()
        m = win32file.ReadFile(self.handle, 65535, None)
        return m

    def _read_thread(self):
        while not self._event.is_set():
            m = self._read()
            self._queue.put(m)

    def read(self, timeout=None):
        return self._queue.get(timeout=timeout)

    def __str__(self):
        return self.format_name()

    def close(self):
        win32pipe.DisconnectNamedPipe(self.handle)

    __repr__ = __str__

    def __enter__(self):
        self._connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class _Writer:

    def format_name(self):
        return fr"\\.\pipe\{self.name}"

    def _write_thread(self):
        while not self._event.is_set():
            m = self._queue.get()
            self.write(m)

    def __init__(self, name):
        self.name = name
        self.handle = None

        self._queue = Queue()
        self._event = Event()

        self._connect()

    def _connect(self):
        """
        链接至命名管道
        :return:
        """
        self.handle = win32file.CreateFileW(
            self.format_name(),
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

    def write(self, data):
        m = win32file.WriteFile(self.handle, json.dumps(data).encode())
        return m

    def __str__(self):
        return self.format_name()

    def close(self): win32file.CloseHandle(self.handle)

    __repr__ = __str__

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def Writer(name):
    try:
        w = _Writer(name)
        return w
    except Exception as e:
        return None


def Reader(name):
    try:
        r = _Reader(name)
        return r
    except Exception as e:
        return None


def create(name):
    r = Reader(name)
    w = Writer(name)
    return r, w


def send(pipe_name, msg):
    w = Writer(pipe_name)
    w.write(msg)
    w.close()


def read(pipe_name):
    r = Reader(pipe_name)
    m = r.read()
    r.close()
    return m


