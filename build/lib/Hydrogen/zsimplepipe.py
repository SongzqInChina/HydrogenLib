# 操作Windows的os.pipe()返回的管道

import os
import queue
from collections import deque

from . import zthread, zjson


# module end


class _PIPEWriter:
    """
    因为pipe是单向的，所以我们需要创建两个类
    """

    def __init__(self, writer: int, buffer_size: int = 1024):
        self._pipe = writer
        self._io = os.fdopen(self._pipe, 'w', buffer_size)

        self._msg_queue = queue.Queue(buffer_size)
        self._event = zthread.threading.Event()

        self._write_thread = zthread.start_daemon_thread(self._write_thread_func)

        self.buffersize = buffer_size

    def set(self, pipe: int):
        self._event.set()
        self._io.close()
        self._write_thread.join()
        self._pipe = pipe
        self._io = os.fdopen(self._pipe, 'w', self.buffersize)
        self._event.clear()
        self._write_thread = zthread.start_daemon_thread(self._write_thread_func)

    def write(self, data):
        if data is None or data is ...:
            raise ValueError("You should send 'None' or '...' to the reader, they hava their functions.")
        data_text = zjson.pickle_simple.encode(data)
        self._msg_queue.put(data_text)

    def _write_thread_func(self):
        while not self._event.is_set():
            if not self._msg_queue.empty():
                msg = self._msg_queue.get()
                self._io.write(msg)
                self._io.write('\n')
                self._io.flush()


class _PIPEReader:
    def __init__(self, reader: int):
        self._pipe = reader

        self._io = os.fdopen(reader, 'r')

        self._msg_queue = queue.Queue()
        self._event = zthread.threading.Event()

        self._read_thread = zthread.start_daemon_thread(self._read_thread_func)
        self.errors = deque()

    def set(self, reader):
        self._event.set()
        self._read_thread.join()
        self._io.close()
        self._pipe = reader
        self._io = os.fdopen(self._pipe, 'r')
        self._event.clear()
        self._read_thread = zthread.start_daemon_thread(self._read_thread_func)

    def read(self, timeout: int | None = ...):
        if timeout is ...:
            timeout = None
        try:
            return self._msg_queue.get(timeout=timeout)
        except queue.Empty as e:
            print("EmptyError:", e)
        except TimeoutError as e:
            print("TimeoutError:", e)

    def _read_thread_func(self):
        while not self._event.is_set():
            try:
                one_data = self._io.readline()
                unpacking_data = zjson.pickle_simple.decode(one_data)
                self._msg_queue.put(unpacking_data)
            except Exception as e:
                self.errors.append(e)


def writer(pipe: int, buffer_size: int = 65535):
    return _PIPEWriter(pipe, buffer_size)


def reader(pipe: int):
    return _PIPEReader(pipe)


def get_pair(os_pipe: tuple[int, int], buffer_size: int = 65535):
    return reader(os_pipe[0]), writer(os_pipe[1], buffer_size)
