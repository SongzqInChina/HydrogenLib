import threading
from typing import Callable, Any

import jsonpickle as json
import win32file
import win32pipe

# module end

class _Reader:
    _lock = threading.Lock()

    def format_name(self):
        return fr"\\.\pipe\{self.name}"

    def __init__(self, name):
        self.name = name
        self.handle = win32pipe.CreateNamedPipe(
            self.format_name(),
            win32pipe.PIPE_ACCESS_INBOUND,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65535, 65535,
            0, None
        )

    def connect(self):
        win32pipe.ConnectNamedPipe(self.handle, None)

    def read(self):
        self._lock.acquire()
        m = win32file.ReadFile(self.handle, 65535, None)
        self._lock.release()
        return m

    def processing(self):
        return json.loads(self.read()[1].decode())

    def __str__(self):
        return self.format_name()

    def close(self):
        win32pipe.DisconnectNamedPipe(self.handle)

    __repr__ = __str__

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class _Writer:
    _lock = threading.Lock()

    def format_name(self):
        return fr"\\.\pipe\{self.name}"

    def __init__(self, name):
        self.name = name
        self.handle = None

    def connect(self):
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
        self._lock.acquire()
        m = win32file.WriteFile(self.handle, json.dumps(data).encode())
        self._lock.release()
        return m

    def __str__(self):
        return self.format_name()

    def close(self): win32file.CloseHandle(self.handle)

    __repr__ = __str__

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def Writer(name):
    try:
        w = _Writer(name)
        w.connect()
        return w
    except Exception as e:
        return None


def Reader(name):
    try:
        r = _Reader(name)
        r.connect()
        return r
    except Exception as e:
        return None


def create(name):
    r = Reader(name)
    w = Writer(name)
    r.connect()
    w.connect()
    return r, w


def send(pipe_name, msg):
    w = Writer(pipe_name)
    w.connect()
    w.write(msg)
    w.close()


def read(pipe_name):
    r = Reader(pipe_name)
    r.connect()
    m = r.processing()
    r.close()
    return m


class _Info:
    def __init__(self, class_, text, json_decode):
        self._class = class_
        self._text = text
        self._json = json_decode

    @property
    def object(self):
        return self._class

    @property
    def text(self):
        return self._text

    @property
    def json(self):
        return self._json

    @property
    def decode(self):
        return self._json.loads(self._text[1])


class _Listener:
    def __init__(self, reader: _Reader, callback: Callable[[Any], bool]):
        self._class = reader
        self._callback = callback
        self._thread: None | threading.Thread = None
        self._stop = False

    def listen(self):
        self._stop = False

        def wrap():
            while not self._stop:
                m = self._class.read()
                i = _Info(self._class, m, json)
                if not self._callback(i):
                    break

        self._thread = threading.Thread(target=wrap, name=f'Lister(name="{self._class.format_name()}")')
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread.is_alive():
            raise "Can't stop the lister!"


def listener(reader, callback):
    return _Listener(reader, callback)
