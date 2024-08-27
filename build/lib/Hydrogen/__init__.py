import logging
import os
import sys

from . import zout, ztime


# TODO: Improve the zout module


class _LogFormat(logging.Formatter):
    def format(self, record):
        message = record.getMessage()
        error_level = record.levelname
        data_time = ztime.time.asctime()
        color_head = ''
        if error_level == "ERROR":
            color_head = zout.get_color_head(255, 0, 0)
        elif error_level == "WARNING":
            color_head = zout.get_color_head(255, 255, 0)
        elif error_level == "INFO":
            color_head = zout.get_color_head(0, 255, 0)
        elif error_level == "DEBUG":
            color_head = zout.get_color_head(0, 0, 255)
        elif error_level == "CRITICAL":
            color_head = zout.get_color_head(255, 0, 255)
        elif error_level == "NOTSET":
            color_head = zout.get_color_init()

        return color_head + f"Module {record.module} at '{data_time}' Logging: [{error_level}] - {message}" + zout.get_color_init()


_lib_logging_root = logging.getLogger()
Formatter = _LogFormat()
_lib_logging_root.setLevel(logging.DEBUG)

version = "0.0.1"

_lib_logging_root.debug("--Qzlib-------------------------")
_lib_logging_root.debug(f"| version:\t{version}")
_lib_logging_root.debug(f"| platform:\t{os.name}")
_lib_logging_root.debug(f"| python:\t{sys.version}")
_lib_logging_root.debug(f"--log--------------------------")


def management_logger():
    return _lib_logging_root


from . import (
    zdatabase,
    # zdatabaseX,  # TODO: This module is not finished  # 这个模块处于半弃坑状态
    zencrypt,  # finished
    zfile,  # finished
    zfilex,  # finished
    zjson,  # finished
    zlibcon,  # finished (dynamic updates)
    znetwork,  # finished
    znamepipe,  # finished
    zother,  # finished
    zpath,  # finished
    zprocess,  # finished
    zprocessx,  # finished
    zreg,  # finished
    zsystem,  # finished
    zconsole,  # finished
    zthread,  # finished
    typefunc,  # finished
    zwindow,  # finished  # Warning: This module has not undergone comprehensive testing
    zstruct,  # finished
    sample,  # finished
    zFileSystemMapper,  # finished
    # zplugins_loader,  # T-O-D-O: This module is not finished # 好吧，这个模块被放弃了
    zauth,  # finished
    zsimplepipe,  # finished
    zhash,  # finished
    zencryio,  # finished
    data_structure,  # finished
    # boardcast_room # 这个模块也没有完成，等把znetwork的功能类在完善和添加后再制作
    ztest,  # finished  # Ztest 模块很有效，但是实现也比较复杂，还有JSON导出和HTML导出还没有做好
    SES,  # finished
)

_lib_logging_root.debug("All modules are ready.")
