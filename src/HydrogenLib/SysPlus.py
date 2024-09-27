import inspect
import logging
import os

import psutil

from .ProcessPlus import Process, ProcessPlus

zsystem_logger = logging.getLogger("SzQlib.zsystem")


def wmi_process():
    return ("win32_process")


def wmi_service():
    return ("win32_service")


def wmi_disk():
    return ("win32_logicaldisk")


def wmi_network():
    return ("win32_networkadapterconfiguration")


def wmi_bios():
    return ("win32_bios")


def wmi_cpu():
    return ("win32_processor")


def wmi_os():
    return ("win32_operatingsystem")


def wmi_user():
    return ("win32_useraccount")


def wmi_group():
    return ("win32_group")


def wmi_group_user():
    return ("win32_groupuser")


def wmi_share():
    return ("win32_share")


if os.name == 'nt':

    def shutdown(mode: str, _time: int = 1):
        if _time < 1:
            _time = 1
        return os.system(f'shutdown -{mode} -t {_time}')


class Runtime:
    _instance = None

    @classmethod
    def __getruntime(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        stact = inspect.stack()[1].function
        if stact != "__getruntime":
            raise RuntimeError("Runtime class can only be instantiated by the getruntime method")
        if cls._instance is None:
            cls._instance = super(Runtime, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        self._c = Process.myClass()

    @property
    def pid(self):
        return self._c.pid

    def cpu_count(self):
        return os.cpu_count()

    def num_threads(self):
        return self._c.num_threads()

    def cpu_percent(self):
        return self._c.cpu_percent()

    def memory_percent(self):
        return self._c.memory_percent()

    def memory_info(self):
        return self._c.memory_info()

    def memory_full_info(self):
        return self._c.memory_full_info()

    def kill(self):
        self._c.kill()

    def exit(self, code):
        exit(code)

    def environ(self):
        return self._c.environ()

    def cmdline(self):
        return self._c.cmdline()

    def exec(self, command):
        return psutil.Popen(command)

    def execute(self, command):
        return ProcessPlus(psutil.Popen(command).pid)

    @classmethod
    def getRuntime(cls):
        return cls.__getruntime()


zsystem_logger.debug("Module zsystem loading ...")
