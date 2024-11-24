import time

from .process import CProcess as _CProcess


class Xfunc:
    ...


class ProcessPlus(Xfunc, _CProcess):
    def pause(self):
        self.suspend()

    def recover(self):
        self.resume()

    def exitcode(self) -> int | None:
        return self.wait()


class Timer(Xfunc):
    def __init__(self):
        self._time = 0
        self._res = 0

    def start(self):
        self._time = time.time()

    def stop(self):
        self._res = time.time() - self._time
        return self._res

    def reset(self):
        self._time = 0
        self._res = 0

    @property
    def res(self):
        return self._res
