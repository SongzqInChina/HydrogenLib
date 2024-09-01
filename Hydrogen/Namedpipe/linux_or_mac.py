# Namedpipe for linux and macos
# TODO: 完成基于FIFO的命名管道伪实现的测试
import fcntl
import os
import time
from queue import Queue
from threading import Event

from Hydrogen.ThreadingPlus import run_with_timeout, start_daemon_thread


# module end, but test not finished

def create_fifo(path):
    try:
        os.mkfifo(path)
    except FileExistsError:
        return


def lock_fifo(fd):
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def unlock_fifo(fd):
    fcntl.flock(fd, fcntl.LOCK_UN)


class _Reader:
    def __init__(self, name):
        self.name = name
        self._event = Event()
        self._queue = Queue()
        self._thread = start_daemon_thread(self._read_thread)

    def _wait(self):
        while not os.path.exists(self.name):
            time.sleep(0.05)

    def wait(self, timeout=None):
        try:
            run_with_timeout(self._wait, timeout)
        except TimeoutError as e:
            raise e

    def _read(self):
        with open(self.name, 'r') as f:
            try:
                lock_fifo(f.fileno())
                data = f.read()
                unlock_fifo(f.fileno())
                return data
            except Exception:
                return None

    def _read_thread(self):
        while not self._event.is_set():
            try:
                data = self._read()
                self._queue.put(data)
            except:
                continue

    def read(self, timeout=None):
        return self._queue.get(timeout=timeout)


class _Writer:
    def __init__(self, name):
        self.name = name
        self._queue = Queue()
        self._event = Event()

        self._thread = start_daemon_thread(self._write_thread)

    def check(self):
        if not os.path.exists(self.name):
            create_fifo(self.name)

    def _write(self, data):
        self.check()
        with open(self.name, 'w') as f:
            try:
                lock_fifo(f.fileno())
                f.write(data)
                unlock_fifo(f.fileno())
            except Exception:
                return

    def _write_thread(self):
        while not self._event.is_set():
            try:
                data = self._queue.get(timeout=0.05)
                self._write(data)
            except Exception as e:
                pass

    def write(self, data):
        self._queue.put(data)

    def close(self):
        os.remove(self.name)


def Reader(name):
    return _Reader(name)


def Writer(name):
    return _Writer(name)


if __name__ == '__main__':
    r = Reader("Test")
    w = Writer("Test")
    r.wait()
    w.write("Hello")
    print(r.read())
