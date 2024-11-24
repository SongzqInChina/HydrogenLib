import copy
import struct

from . import encrypt
from . import type_func


def pack(data):
    """
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
        return struct.pack("<q", data)
    elif data_type == float:
        return struct.pack("<d", data)
    elif data_type == str:
        raise TypeError from TypeError("argument for 's' must be a bytes object")
    elif data_type == bytes:
        return data
    elif data_type == bool:
        return struct.pack("<?", data)
    else:
        raise TypeError("unsupported data type: {}".format(data_type))


def unpack(data_type, data):
    if data_type == int:
        return struct.unpack("<q", data)[0]
    elif data_type == float:
        return struct.unpack("<d", data)[0]
    elif data_type == str:
        return struct.unpack("<s", data)[0]
    elif data_type == bytes:
        return struct.unpack("<p", data)[0]
    elif data_type == bool:
        return struct.unpack("<?", data)[0]
    else:
        raise TypeError("Unsupported data type: {}".format(data_type))


def pack_anylenght(data, lenght=16, max_lenght=False):
    data_type = type(data)
    if data_type == str:
        return encrypt.func.pad(data.encode(), lenght)
    if data_type == int:
        x = copy.copy(data)
        data_bytes = type_func.int_to_bytes(x, lenght, "little")
        if max_lenght:
            return type_func.get_vaild_data(data_bytes)
        return data_bytes
    if data_type == bytes:
        if len(data) <= max_lenght:
            return data
        return encrypt.func.pad(data, lenght)
    if data_type == float:
        int_num, float_int_num = tuple(map(int, str(data).split('.')[:2]))

        int_bytes = pack_anylenght(int_num, 2048, True)
        float_bytes = pack_anylenght(float_int_num, 2048, True)

        try:
            int_len_bytes = pack_anylenght(len(int_bytes), 8)  # 获取int长度
        except OverflowError as e:
            raise OverflowError(f"result's 'int_len_byes' is too long, cannot finish package(you can split the data)")

        result = int_len_bytes + int_bytes + float_bytes

        if len(result) > lenght:
            raise OverflowError(
                f"result is too long, cannot finish package(try to use {len(int_bytes) + len(float_bytes) + 8})")

        if max_lenght:
            return result
        else:
            print(result)
            return encrypt.func.pad(result, lenght)


def unpack_anylenght(data_type, data: bytes, data_lenght, max_lenght=False):
    if not max_lenght and len(data) != data_lenght:
        raise RuntimeError("data length is not equal to data_lenght({} and {})".format(len(data), data_lenght))
    if len(data) == 0:
        return None

    if data_type == int:
        data_int = type_func.bytes_to_int(data)
        return data_int

    if data_type == str:
        return encrypt.func.unpad(data).decode()

    if data_type == bytes:
        if max_lenght:
            return data
        return encrypt.func.unpad(data)

    if data_type == float:
        data_offset = type_func.IndexOffset.Offset(encrypt.func.unpad(data, data_lenght))
        print(encrypt.func.unpad(data, data_lenght))
        int_lenght = unpack_anylenght(int, data_offset.offset(8), 2048, True)
        print("Int Lenght:", int_lenght)

        int_data = unpack_anylenght(int, data_offset.offset(int_lenght), 2048, True)
        print("Int Data:", int_data)
        float_data = unpack_anylenght(int, data_offset.surplus(bytes), 2048, True)
        print("Float Data:", float_data)

        return eval("{}.{}".format(int_data, float_data))
