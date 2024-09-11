# Namedpipe for linux and macos
# TODO: 完成基于FIFO的命名管道伪实现的测试
import fcntl
import os
import time

from Hydrogen.ThreadingPlus import run_with_timeout


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

    def read(self, timeout=None):
        try:
            return run_with_timeout(self._read, timeout)
        except TimeoutError as e:
            raise e


class _Writer:
    def __init__(self, name):
        self.name = name

    def check(self):
        if not os.path.exists(self.name):
            create_fifo(self.name)

    def write(self, data):
        self.check()
        with open(self.name, 'w') as f:
            try:
                lock_fifo(f.fileno())
                f.write(data)
                unlock_fifo(f.fileno())
            except Exception:
                pass

    def close(self):
        os.remove(self.name)


def Reader(name):
    return _Reader(name)


def Writer(name):
    return _Writer(name)
