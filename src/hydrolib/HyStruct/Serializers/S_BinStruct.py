import builtins
from typing import final

from . import Abc
from ... import auto_struct
from ... import type_func


class BinStruct:
    """

    # 二进制结构体基类

    方法:
        - pack() **不可覆写**, 打包结构体
        - unpack(data) **不可覆写** 解包结构体,返回一个以cls为基类的新结构体实例(新返回的结构体实例的类型与打包时的结构体类型会不一致)
            比如:
                ```python
                class Test(BinStruct):
                    _data_ = ['data']
                    data = 0

                ins = Test(data=10)
                packed_data = ins.pack()
                new_ins = Test.unpack(packed_data)
                print(ins.__class__ is new_ins.__class__)  # False
                ```
            虽然类型名称一样,但是实际类型不一样
            具体实现可查看源码(/src/HydrogenLib/HyStruct/S_BinStruct.py)
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
        this_name = self.__class__.__name__
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

    @classmethod
    @final
    def unpack(cls, data):
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
        ins = type(this_name, (cls,), dct)
        ins._data_ = list(dct.keys())
        return ins()

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
