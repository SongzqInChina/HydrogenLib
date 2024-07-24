import threading


# module end

class _ThreadPipe(threading.Event):
    def __init__(self):
        super().__init__()
        self._data = None

    def write(self, data):
        self._data = data
        super().set()

    def read(self):
        super().wait()
        data = self._data
        self._data = None
        super().clear()
        return data


class _ThreadPipeWriter:
    def __init__(self, pipe):
        self._pipe = pipe

    def write(self, data):
        self._pipe.write(data)


class _ThreadPipeReader:
    def __init__(self, pipe):
        self._pipe = pipe

    def read(self):
        return self._pipe.read()


def Pipe():
    pipe = _ThreadPipe()
    return _ThreadPipeReader(pipe), _ThreadPipeWriter(pipe)


class Lock(threading.Lock):
    ...


class RLock(threading.RLock):
    ...
