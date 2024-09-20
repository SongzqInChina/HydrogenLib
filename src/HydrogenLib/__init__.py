from . import _error_hook
from .Classes.Version import Version as _Version
_error_hook.init()

import logging
import os
import sys

from . import OutputPlus, Time

version = _Version.from_file(r".\Resources\version")


class _LogFormat(logging.Formatter):
    def format(self, record):
        message = record.getMessage()
        error_level = record.levelname
        data_time = Time.time.asctime()
        color_head = ''
        if error_level == "ERROR":
            color_head = OutputPlus.get_color_head(255, 0, 0)
        elif error_level == "WARNING":
            color_head = OutputPlus.get_color_head(255, 255, 0)
        elif error_level == "INFO":
            color_head = OutputPlus.get_color_head(0, 255, 0)
        elif error_level == "DEBUG":
            color_head = OutputPlus.get_color_head(0, 0, 255)
        elif error_level == "CRITICAL":
            color_head = OutputPlus.get_color_head(255, 0, 255)
        elif error_level == "NOTSET":
            color_head = OutputPlus.color_init()

        return color_head + f"Module {record.module} at '{data_time}' Logging: [{error_level}] - {message}" + OutputPlus.color_init()


_lib_logging_root = logging.getLogger()
Formatter = _LogFormat()
_lib_logging_root.setLevel(logging.DEBUG)

_lib_logging_root.debug("--HydrogenLib-------------------------")
_lib_logging_root.debug(f"| version:\t{version}")
_lib_logging_root.debug(f"| platform:\t{os.name}")
_lib_logging_root.debug(f"| python:\t{sys.version}")
_lib_logging_root.debug(f"--log--------------------------")


def management_logger():
    return _lib_logging_root


from . import (
    Database,
    Encrypt,  # finished
    File,  # finished
    Json,  # finished
    Const,  # finished (dynamic updates)
    SocketPlus,  # finished
    Namedpipe,  # finished
    # Classes,  # finished
    PathPlus,  # finished
    Process,  # finished
    ProcessPlus,  # finished
    WinregPlus,  # finished
    SysPlus,  # finished
    ThreadingPlus,  # finished
    TypeFunc,  # finished
    Win32Window,  # finished  # Warning: This module has not undergone comprehensive testing
    StructPlus,  # finished
    SampleData,  # finished
    # zplugins_loader, # 好吧，这个模块被放弃了 转到附属项目Hy20 Loader
    Auth,  # finished
    PipePlus,  # finished
    Hash,  # finished
    Encryio,  # finished
    DataStructures,  # finished
    # boardcast_room # 这个模块也没有完成，等把znetwork的功能类在完善和添加后再制作
    TestManager,  # 重制中
    SES,  # finished
    EnhanceToml,  # not finish
)

_lib_logging_root.debug("All modules are ready.")
__all__ = [
    'Auth',
    'Const',
    'Database',
    'Decorators',
    'Encryio',
    'EnvPlus',
    'Example',
    'File',
    'Hash',
    'ImportPlus',
    'Json',
    'LoggingPlus',
    'Network',
    'OutputPlus',
    'PathPlus',
    'PipePlus',
    'Process',
    'ProcessPlus',
    'SocketPlus',
    'StructPlus',
    'SysPlus',
    'ThreadingPlus',
    'Time',
    'WinregPlus',
    'ABC',
    # 'BoardcastRoom'
    'Classes',
    'DataStructures',
    'Encrypt',
    'Namedpipe',
    'SampleData',
    'SES',
    'TestManager',
    'TypeFunc',
    'Win32Window'
]
