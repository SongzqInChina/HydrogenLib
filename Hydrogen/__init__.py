import logging
import os
import sys

from . import OutputPlus, Time


# TODO: Improve the OutputPlus module


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
            color_head = OutputPlus.get_color_init()

        return color_head + f"Module {record.module} at '{data_time}' Logging: [{error_level}] - {message}" + OutputPlus.get_color_init()


_lib_logging_root = logging.getLogger()
Formatter = _LogFormat()
_lib_logging_root.setLevel(logging.DEBUG)

version = "0.1.0"

_lib_logging_root.debug("--Qzlib-------------------------")
_lib_logging_root.debug(f"| version:\t{version}")
_lib_logging_root.debug(f"| platform:\t{os.name}")
_lib_logging_root.debug(f"| python:\t{sys.version}")
_lib_logging_root.debug(f"--log--------------------------")


def management_logger():
    return _lib_logging_root


from . import (
    Database,
    # zdatabaseX,  # TODO: This module is not finished  # 这个模块处于半弃坑状态
    Encrypt,  # finished
    File,  # finished
    Json,  # finished
    Const,  # finished (dynamic updates)
    SocketPlus,  # finished
    Namedpipe,  # finished
    Classes,  # finished
    PathPlus,  # finished
    Process,  # finished
    ProcessPlus,  # finished
    WinregPlus,  # finished
    SysPlus,  # finished
    ConsolePlus,  # finished
    ThreadingPlus,  # finished
    TypeFunc,  # finished
    Win32Window,  # finished  # Warning: This module has not undergone comprehensive testing
    StructPlus,  # finished
    SampleData,  # finished
    FileSystemMapper,  # finished
    # zplugins_loader,  # T-O-D-O: This module is not finished # 好吧，这个模块被放弃了
    Auth,  # finished
    PipePlus,  # finished
    Hash,  # finished
    Encryio,  # finished
    DataStructures,  # finished
    # boardcast_room # 这个模块也没有完成，等把znetwork的功能类在完善和添加后再制作
    TestManager,  # finished  # Ztest 模块很有效，但是实现也比较复杂，还有JSON导出和HTML导出还没有做好
    SES,  # finished
)

_lib_logging_root.debug("All modules are ready.")
