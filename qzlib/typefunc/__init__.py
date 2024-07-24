from typing import Literal

from . import (
    dict,
    list,
    template,
    index_offset,
    binaryTree,
    func,
)


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
