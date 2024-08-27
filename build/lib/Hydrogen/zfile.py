import logging

import win32api
import win32con

zfile_logger = logging.getLogger(__name__)


# module end

def create_file(file, text="", clean: bool = True):
    """
    创建一个文件并写入数据
    :param file:
    :param text:
    :param clean:
    :return:
    """
    zfile_logger.debug(f"Create a new file: {file}, text={repr(text)}")
    f = open(file, 'w' if clean else 'a')
    f.write(text)


def get_path(__file__=__file__):
    """
    获取一个文件的父目录
    :param __file__:
    :return:
    """
    if '/' in __file__:
        return "\\".join(__file__.split('/')[0:-1:]) + '\\'
    else:
        return '\\'.join(__file__.split('\\')[0:-1:]) + '\\'


def hideFile(path):
    """
    隐藏文件
    :param path:
    :return:
    """
    win32api.SetFileAttributes(str(path), win32con.FILE_ATTRIBUTE_HIDDEN)


def onlyReadFile(Path):
    """
    设置文件为只读
    :param Path:
    :return:
    """
    win32api.SetFileAttributes(str(Path), win32con.FILE_ATTRIBUTE_READONLY)


def rwFile(Path):
    """
    设置文件为读写
    :param Path:
    :return:
    """
    win32api.SetFileAttributes(Path, win32con.FILE_ATTRIBUTE_ARCHIVE)


zfile_logger.debug("Module zfile loading ...")
