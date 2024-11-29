import builtins
import sys
from typing import final

from . import Abc
from ... import auto_struct
from ... import type_func

from rich import print


def _get_class(equal_name: str):
    cls = type_func.get_attr_by_path(equal_name, {'builtins': builtins, **sys.modules})
    return cls


def _get_type_equal_name(obj):
    typ = type(obj)
    module = typ.__module__
    name = typ.__qualname__
    return module + '.' + name


class BinStruct:
    """

    # 二进制结构体基类

    方法:
        - pack() **不可覆写**, 打包结构体
        - unpack(data) **不可覆写** 解包结构体
    属性:
        - _data_ 需要打包的属性**列表**
    """
    _data_ = []  # Variables' names

    def __init__(self, *args, **kwargs):
        names = set()
        for name, value in zip(self._data_, args):
            setattr(self, name, value)
            names.add(name)

        for name, value in kwargs.items():
            if name in names:
                raise ValueError(f'Duplicate name: {name}')
            setattr(self, name, value)

    @final
    def pack(self):
        res = b''
        this_name = _get_type_equal_name(self)
        this_length = len(this_name)
        res += bytes([this_length]) + this_name.encode()
        for name in self._data_:
            origin_data = getattr(self, name)
            if isinstance(origin_data, BinStruct):
                packed_data = origin_data.pack()
                type_name = 'BinStruct'
            else:
                packed_data = auto_struct.pack(origin_data)
                type_name = type_func.get_type_name(origin_data)
            length_1 = len(name)
            length_2 = len(packed_data)
            length_3 = len(type_name)
            res += bytes([length_1, length_2, length_3]) + name.encode() + packed_data + type_name.encode()
        return res

    @staticmethod
    @final
    def unpack(data):
        offset = type_func.IndexOffset.Offset(data)
        this_length = type_func.bytes_to_int(offset > 1)
        this_name = (offset > this_length).decode()
        dct = {}

        while not offset.isend():
            length_1, length_2, length_3 = offset > 1, offset > 1, offset > 1
            name = (offset > length_1[0]).decode()
            packed_data = offset > length_2[0]
            type_name = (offset > length_3[0]).decode()

            if type_name == 'BinStruct':
                origin_data = BinStruct.unpack(packed_data)
            else:
                origin_data = auto_struct.unpack(getattr(builtins, type_name), packed_data)
            dct[name] = origin_data
        typ = _get_class(this_name)
        print(typ, this_name)
        return typ(**dct)

    def __gets(self):
        dct = {}
        for name in self._data_:
            dct[name] = getattr(self, name)
        return dct

    def __str__(self):
        kv_pairs = list(self.__gets().items())
        return f'{self.__class__.__name__}({", ".join((f"{name}={value}" for name, value in kv_pairs))})'

    __repr__ = __str__


class Struct(Abc.Serializer):
    struct = BinStruct

    def dumps(self, data):
        return data.pack()

    def loads(self, data):
        return self.struct.unpack(data)
