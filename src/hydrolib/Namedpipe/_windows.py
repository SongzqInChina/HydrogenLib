import re

import win32file
import win32pipe


def is_pipe_path(path: str):
    r"""
    检查是否是一个标准的pipe路径

    一个标准的Pipe路径应为:``\\.\pipe\pipe_name``

    或者：``\\?\pipe\pipe_name``

    且，pipe路径不允许包含子文件夹，Pipe路径中的pipe_name不能为空


    :param path: 待检查的Pipe路径
    :return: Bool值，表示是否为标准Pipe路径
    """
    match_str = re.match(r"(\\\\([.?])\\pipe\\)[^\\/\s()\"\[\]*$%^`]+$", path)
    return match_str is not None


def format_pipe_name(name: str):
    """
    格式化Pipe名称为Pipe路径
    如果传入参数被确认已经是Pipe路径，那么直接返回
    :param name: 待格式化的名称，不能为空字符序列
    :return:
    """
    if name.isspace():
        raise ValueError("Pipe name cannot be empty")
    if is_pipe_path(name):
        return name
    return fr"\\.\pipe\{name}"


def get_pipe_object(name, buffer_size=65535, max_instances=1):
    return win32pipe.CreateNamedPipe(
        format_pipe_name(name),
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        max_instances,
        buffer_size,
        buffer_size,
        0,
        None
    )


def get_pipe_handle(name):
    return win32file.CreateFile(
        format_pipe_name(name),
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        0,
        None,
        win32file.OPEN_EXISTING,
        0,
        None
    )


class _Reader:
    def __init__(self, name):
        self.name = name
        self.filename = format_pipe_name(name)


if __name__ == '__main__':
    print(is_pipe_path(r"\\.\pipe\Pipe"))
    print(is_pipe_path(r"\\.\pipe\Pipe\adadf"))
    print(is_pipe_path(r"\\.\pipe\x df"))
    print(is_pipe_path(r"\\.\pipe\&dfaf"))
