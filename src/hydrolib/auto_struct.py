import struct
from typing import Tuple

from . import type_func


def pack(data):
    """
    对基本Struct模块的功能进行一定的改进的方法
    **Format Mro**

    - x           pad byte
    - c           char
    - b           int8
    - B           uint8
    - h           int16
    - H           uint16
    - i           int32
    - I           uint32
    - l           int64
    - L           uint64
    - f           float
    - d           double
    - s           char[]
    - q           long long
    - Q           unsigned long long
    - e           half float
    - f           float
    - d           double
    - n           long long
    - N           unsigned long long
    - p           bytes
    - P           int(Point)
    - ?           bool
    """
    data_type = type(data)
    if data_type == int:
        return type_func.int_to_bytes_nonelength(data)
    elif data_type == float:
        return struct.pack("<d", data)
    elif data_type == str:
        return data.encode()
    elif data_type == bytes:
        return data
    elif data_type == bool:
        return struct.pack("<?", data)
    else:
        raise TypeError("unsupported data type: {}".format(data_type))


def unpack(data_type, data):
    if data_type == int:
        return type_func.bytes_to_int(data)
    elif data_type == float:
        return struct.unpack("<d", data)[0]
    elif data_type == str:
        return data.decode()
    elif data_type == bytes:
        return data
    elif data_type == bool:
        return struct.unpack("<?", data)[0]
    else:
        raise TypeError("Unsupported data type: {}".format(data_type))


def pack_variable_length_int(x: int):
    """
    将整数打包为可变长格式
    """
    res = bytearray()
    while True:
        byte = x & 0x7F
        x >>= 7
        if x:
            byte |= 0x80
        res.append(byte)
        if not x:
            break
    return bytes(res)


def unpack_variable_length_int(data: bytes) -> Tuple[int, int]:
    """
    将可变长格式的整数字节串解包
    """
    result = 0
    shift = 0
    count = 0
    for byte in data:
        result |= (byte & 0x7F) << shift
        shift += 7
        if byte & 0x80 == 0:
            break
        count += 1
    return result, count + 1

