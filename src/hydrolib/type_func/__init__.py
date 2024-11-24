from typing import Literal

from . import (
    Dict,
    List,
    Template,
    IndexOffset,
    BinaryTree,
    Func,
)
from ..data_structures import Stack


def int_to_bytes(num, lenght, byteorder='little'):
    try:
        byte = num.to_bytes(lenght, byteorder)
    except OverflowError as e:
        raise e
    return byte


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


def get_attr_by_path(obj, path):
    """

    根据一个引用路径获取对象，返回一个引用栈

    如``get_attr_by_path(obj, "attr1.attr2.attr3")``返回一个``Stack([obj, value1, value2, value3])``

    如果你希望从globals中获取对象，你可以先把globals字典转换为一个``Namespace``，然后调用函数获取对象


    :param obj: 初始根对象
    :param path: 引用路径

    """
    path_list = path.split('.')
    cur_obj = obj
    s = Stack([cur_obj])
    while len(path_list):
        cur_obj = getattr(cur_obj, path_list.pop(-1))
        s.push(cur_obj)

    return s


def get_type_name(origin_data):
    return origin_data.__class__.__name__