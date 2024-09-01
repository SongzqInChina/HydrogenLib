import os
import time

import psutil

from .Process import CProcess as _CProcess
from .Process import kill_process_by_pid, kill_process_by_name, ProcessInfo


class Xfunc:
    ...


class CProcess(Xfunc, _CProcess):
    def pause(self):
        self.suspend()

    def recover(self):
        self.resume()

    def exitcode(self) -> int | None:
        return self.wait()


class Process(Xfunc):
    @staticmethod
    def KillById(pid):
        kill_process_by_pid(pid)

    @staticmethod
    def killByName(name):
        NAME_killPrcess(name)

    @staticmethod
    def isactiveById(pid):
        return pid in psutil.pids()

    @staticmethod
    def isactiveByName(name):
        for pid in psutil.pids():
            if name == psutil.Process(pid).name():
                return True
        return False

    @staticmethod
    def get(pid):
        if Process.isactiveById(pid):
            return psutil.Process(pid)
        else:
            return None

    @staticmethod
    def getByName(name):
        for pid in psutil.pids():
            if name == psutil.Process(pid).name():
                return psutil.Process(pid)
        return None

    @staticmethod
    def getInfo(pid):
        return ProcessInfo(CProcess(pid))

    @staticmethod
    def getRuntimes(pid):
        return ProcessInfo(CProcess(pid)).runtime()

    @staticmethod
    def getCreatetime(pid):
        return ProcessInfo(CProcess(pid)).create_time()

    @staticmethod
    def getUsername(pid):
        return ProcessInfo(CProcess(pid)).username()

    @staticmethod
    def getProcessName(pid):
        return ProcessInfo(CProcess(pid)).name()

    @staticmethod
    def myPid():
        return os.getpid()

    @staticmethod
    def myClass():
        return CProcess(Process.myPid())


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
