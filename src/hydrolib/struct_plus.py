from typing import Any

from . import type_func
from . import auto_struct as ostruct
from .json import Pickle


def simple_pack(data_bytes: bytes):
    data_len = len(data_bytes)
    data_len_bytes = ostruct.pack(data_len)
    return data_len_bytes + data_bytes


def simple_unpack(data: bytes) -> bytes:
    data_offset = type_func.IndexOffset.Offset(data)
    data_length = ostruct.unpack(int, data_offset > 8)
    return data_offset.offset(data_length)


def simple_unpacks(data: bytes):
    data_offset = type_func.IndexOffset.Offset(data)
    data_length = ostruct.unpack(int, data_offset > 8)
    one_data = data_offset.offset(data_length)
    if data_offset.isend():
        return [one_data]
    else:
        return [one_data, *simple_unpacks(bytes([*data_offset.iterable]))]


def simple_unpack_one(data: bytes):
    data_offset = type_func.IndexOffset.Offset(data)
    data_length = ostruct.unpack(int, data_offset > 8)
    return (data_offset.offset(data_length)), bytes(list(data_offset))


def jsonpickle_pack(data: Any):
    jsonpickle_data = Pickle.encode(data)
    return simple_pack(jsonpickle_data.encode())


def jsonpickle_unpack(data: bytes):
    orial_data = simple_unpack(data)
    return Pickle.decode(orial_data.decode())


def jsonpickle_unpacks(data: bytes):
    orial_data_list = simple_unpacks(data)
    return [Pickle.decode(x.decode()) for x in orial_data_list]


def jsonpickle_unpack_one(data: bytes):
    orial_one_data, data_ = simple_unpack_one(data)
    return Pickle.decode(orial_one_data.decode()), data_
