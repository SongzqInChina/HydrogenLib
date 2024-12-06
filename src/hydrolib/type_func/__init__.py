from typing import Literal

from .BinaryTree import *
from .Bitmap import *
from .Dict import *
from .Func import *
from .IndexOffset import *
from .List import *
from .LiteralEval import *
from .Number import *
from .Template import *
from .Type import *


def int_to_bytes(num: int, lenght, byteorder='little'):
    try:
        byte = num.to_bytes(lenght, byteorder)
    except OverflowError as e:
        raise e
    return byte


def int_to_bytes_nonelength(num: int):
    length = len(hex(num))
    length = max(length // 2 - 1, 1)  # 十六进制下,每两个字符占一个字节
    return num.to_bytes(length, 'little')


def bytes_to_int(data: bytes, byteorder: Literal["little", "big"] = 'little'):
    if len(data) == 0 or not any(data):
        return
    return int.from_bytes(data, byteorder)


def get_vaild_data(data: bytes) -> bytes:
    """
    100100 -> vaild = 1001
    111100 -> vaild = 1111
    :param data:
    :return:
    """
    # 找到第一个有效数据（逆序），他的后面就是无效数据
    after_data = data[::-1]
    for index, value in enumerate(after_data):
        if value != 0:
            last_invaild = len(data) - index
            return data[:last_invaild]
    return b''


def is_errortype(exception) -> bool:
    return isinstance(exception, Exception)


def get_attr_by_path(path, Globals=None, Locals=None):
    """
    :param path: 引用路径
    :param Globals: globals() 字典
    :param Locals: locals() 字典

    """
    try:
        return LiteralEval.literal_eval(path, Globals, Locals)
    except (NameError, ValueError, SyntaxError, TypeError, Exception):
        return None


def get_type_name(origin_data):
    return origin_data.__class__.__name__
