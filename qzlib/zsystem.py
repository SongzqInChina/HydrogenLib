import copy
import inspect
import logging
import os
from typing import Sequence, Generator

import psutil
from win32com import client

from .zprocessx import Process, CProcess

zsystem_logger = logging.getLogger("SzQlib.zsystem")


def wmi():
    return client.GetObject("winmgmts:")


def wmi_process():
    return wmi().InstancesOf("win32_process")


def wmi_service():
    return wmi().InstancesOf("win32_service")


def wmi_disk():
    return wmi().InstancesOf("win32_logicaldisk")


def wmi_network():
    return wmi().InstancesOf("win32_networkadapterconfiguration")


def wmi_bios():
    return wmi().InstancesOf("win32_bios")


def wmi_cpu():
    return wmi().InstancesOf("win32_processor")


def wmi_os():
    return wmi().InstancesOf("win32_operatingsystem")


def wmi_user():
    return wmi().InstancesOf("win32_useraccount")


def wmi_group():
    return wmi().InstancesOf("win32_group")


def wmi_group_user():
    return wmi().InstancesOf("win32_groupuser")


def wmi_share():
    return wmi().InstancesOf("win32_share")


def shutdown(mode: str, _time: int = 1):
    if _time < 1:
        _time = 1
    return os.system(f'shutdown -{mode} -t {_time}')


class EnvVar:
    @staticmethod
    def to_list(__value, __value_sep: str = ';'):
        return [i for i in __value.split(__value_sep) if not i.isspace() and i]

    def __init__(self, __key, __v, __value_sep: str = ';'):
        self._value_sep = __value_sep
        self.key = __key
        self._value = __v
        # 解析value为列表
        self._value_list = self.to_list(self._value, self._value_sep)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self._value_list = self.to_list(self._value, self._value_sep)

    @property
    def key(self):
        return self.key

    @property
    def value_list(self):
        return self._value_list.copy()

    @value_list.setter
    def value_list(self, v):
        self._value_list = v
        self._value = self._value_sep.join(self._value_list)

    def set(self, index, value: str):
        """
        set a new value to `env var`

        :param index: index of env var
        :param value: new value
        :raise ValueError: if ';' in your value
        """
        if self._value_sep in value:
            raise ValueError(f"value must not contain '{self._value_sep}'")
        if index >= len(self._value_list):
            return self._value_list.append(value)
        self._value_list[index] = value

    def pop(self, index):
        if index >= len(self._value_list):
            raise IndexError(f'index out of range: {index}')
        return self._value_list.pop(index)

    def remove(self, _item):
        if _item not in self._value_list:
            raise ValueError(f'{_item} not in env var')
        self._value_list.remove(_item)

    def insert(self, index, value: str):
        self._value_list.insert(index, value)

    def append(self, value: str):
        self._value_list.append(value)

    def get(self, index):
        if index >= len(self._value_list):
            raise IndexError(f'index out of range: {index}')
        return self._value_list[index]

    def clear(self):
        self._value_list = []

    def load(self, string: str | None = None):
        if string is None:
            self._value_list = self.to_list(self._value, self._value_sep)
        else:
            self._value_list = self.to_list(string, self._value_sep)

    @classmethod
    def to_var(cls, key, value, value_sep=';'):
        return cls(key, value, __value_sep=value_sep)

    def __str__(self):
        return self._value_sep.join(self._value_list)

    __repr__ = __str__


class EnvClass:
    def __init__(self, _vars: Sequence[EnvVar]):
        self._vars = {v.key: v for v in _vars}  # type: dict[str, EnvVar]

    def add(self, var: EnvVar):
        if var.key not in self._vars:
            self._vars[var.key] = var

    def add_str(self, key: str, value: str, va_sep=';'):
        if key not in self._vars:
            self._vars[key] = make_var(key, value, va_sep)

    def remove(self, var: EnvVar):
        if var.key in self._vars:
            self._vars.pop(var.key)

    def delete_key(self, key: str):
        if key in self._vars:
            self._vars.pop(key)

    def get(self, key: str):
        return self._vars[key] if key in self._vars else None

    def to_text(self, key: str):
        return str(self._vars[key])

    def text(self) -> Generator[tuple[str, str], None, None]:
        return ((k, str(v)) for k, v in self._vars.items())

    @classmethod
    def to_env(cls, env_dic, va_sep=';'):
        if isinstance(env_dic, os.environ.__class__):
            o = []
            for k, v in env_dic.copy().items():
                o.append(EnvVar.to_var(k, v, value_sep=va_sep))
            return cls(o)
        elif isinstance(env_dic, cls):
            return copy.deepcopy(env_dic)
        elif isinstance(env_dic, dict):
            # 假设就是一个环境变量字典
            o = [EnvVar.to_var(k, v, value_sep=va_sep) for k, v in env_dic.items()]
            return cls(o)


class EnvPool:
    def __init__(self, first_env: EnvClass, name="Base"):
        self._envs = {name: first_env}  # type: dict[str, EnvClass]
        self._copy_osenv()

    def add(self, env: EnvClass, name: str):
        """
        Create a new Env Class
        """
        if name not in self._envs:
            self._envs[name] = env
        else:
            raise ValueError(f"""Env Class '{name}' exists. """)

    def delete(self, name: str):
        if name in self._envs:
            del self._envs[name]
        else:
            raise ValueError(f"""Env Class '{name}' doesn't exist.""")

    def _copy_osenv(self):
        self._osenvbak = vars(os.environ).copy()

    def _set_osenv(self, env_dic: dict, resume=True):
        if not resume:
            self._copy_osenv()
        os.environ.clear()
        os.environ.update(env_dic)

    def activate(self, name: str):
        osenviron = {
            k: v
            for k, v in self._envs[name].text()
        }
        self._set_osenv(osenviron, False)

    def resume(self):
        """
        resume to os.environ
        """
        self._set_osenv(self._osenvbak)


def get_new_pool():
    return EnvPool(EnvClass.to_env(os.environ))


def make_env(env_dic, va_sep=';'):
    return EnvClass.to_env(env_dic, va_sep)


def make_var(key, value, va_sep=';'):
    return EnvVar.to_var(key, value, va_sep)


def os_env_dict():
    return vars(os.environ).copy()


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
        return CProcess(psutil.Popen(command).pid)


    @classmethod
    def getRuntime(cls):
        return cls.__getruntime()


zsystem_logger.debug("Module zsystem loading ...")
