import builtins
import sys
from typing import final, Optional

from . import Abc
from ... import auto_struct
from ... import type_func, struct_plus
from ...utils.Auto import AutoRegDict


class GeneraterError(Exception):
    ...


class UnpackError(Exception):
    ...


def _get_class(equal_name: str):
    cls = type_func.get_attr_by_path(equal_name, {'builtins': builtins, **sys.modules})
    return cls


def _get_type_equal_name(obj):
    typ = type(obj)
    module = typ.__module__
    name = typ.__qualname__
    return module + '.' + name


def _get_attr_bitmap_length(number_of_attrs: int):
    return (number_of_attrs + 7) // 8


length_bytes_settings = {
    'TypeName': 2,
    'AttrName': 2,
    'AttrValue': 2,
    'AttrType': 2,
}


class _PackerAndUnpacker:
    def __pack_int(self, num):
        return type_func.int_to_bytes_nonelength(num)

    def __pack_str(self, string):
        return string.encode()


class BinStruct:
    """

    # 二进制结构体基类

    方法:
        - pack() **不可覆写**, 打包结构体
        - unpack(data) 解包结构体
    属性:
        - _data_ 需要打包的属性**列表**

    """
    __data__ = []  # Variables' names

    def pack_event(self, *args, **kwargs):
        """
        打包事件,进行打包前的处理
        """
        return self.__data__

    def unpack_event(self, *args, **kwargs) -> Optional[Exception]:
        """
        解包事件,解包后对原始数据的重新处理
        """
        pass

    def __init__(self, *args, **kwargs):
        names = set()
        for name, value in zip(self.__data__, args):
            setattr(self, name, value)
            names.add(name)

        for name, value in kwargs.items():
            if name in names:
                raise ValueError(f'Duplicate name: {name}')
            setattr(self, name, value)

    # @final
    # def pack(self):
    #     res = b''
    #     this_name = _get_type_equal_name(self)
    #     this_length = type_func.int_to_bytes(
    #         len(this_name), length_bytes_settings['TypeName']
    #     )
    #     res += this_length + this_name.encode()
    #     for name in self.__data__:
    #         origin_data = getattr(self, name)
    #         if hasattr(self.__class__, name):
    #             if origin_data is getattr(self.__class__, name):
    #                 continue  # 未修改的属性, 跳过
    #         if isinstance(origin_data, BinStruct):
    #             packed_data = origin_data.pack()
    #             type_name = 'BinStruct'
    #         else:
    #             packed_data = auto_struct.pack(origin_data)
    #             type_name = type_func.get_type_name(origin_data)
    #         length_1 = type_func.int_to_bytes(len(name), length_bytes_settings['AttrName'])
    #         length_2 = type_func.int_to_bytes(len(packed_data), length_bytes_settings['AttrValue'])
    #         length_3 = type_func.int_to_bytes(len(type_name), length_bytes_settings['AttrType'])
    #         res += b''.join([length_1, length_2, length_3]) + name.encode() + packed_data + type_name.encode()
    #     return res

    @final
    def pack(self, *args, **kwargs):
        """
        打包结构体
        :param args: 构造函数参数
        :param kwargs: 构造函数参数
        """
        # | Name | AttrMapping | (Value, Type) pairs |

        __data__ = self.pack_event(*args, **kwargs)

        this_name = _get_type_equal_name(self)
        this_length = type_func.int_to_bytes(
            len(this_name), length_bytes_settings['TypeName']
        )
        part_name = this_length + this_name.encode()

        packed_attr_mapping = AutoRegDict()
        packed_attr_mapping.default_value = 0

        for attr in __data__:
            origin_data = getattr(self, attr)
            if hasattr(self.__class__, attr):
                if origin_data is getattr(self.__class__, attr):
                    continue  # 未修改的属性, 跳过
            packed_attr_mapping[attr] = 1

        bitmap = type_func.Bitmap([packed_attr_mapping[attr] for attr in __data__])
        part_bitmap = bitmap.pack()

        part_kvpairs = b''

        for attr, on in packed_attr_mapping.items():
            if not on:
                continue

            value = getattr(self, attr)

            if isinstance(value, BinStruct):
                type_name = value.__class__.__name__
                value = value.pack()

            else:
                type_name = type_func.get_type_name(value)
                value = auto_struct.pack(value)

            length_1 = type_func.int_to_bytes(len(value), length_bytes_settings['AttrValue'])
            length_2 = type_func.int_to_bytes(len(type_name), length_bytes_settings['AttrType'])

            current_part = (
                    length_1 + length_2 + value + type_name.encode()
            )

            part_kvpairs += current_part

        packed_data = (
                part_name + part_bitmap + part_kvpairs
        )
        # print(
        #     'Pack:::\n\t',
        #     'Part::Name=', part_name,
        #     '\n\t',
        #     'Part::Bitmap=', part_bitmap, bitmap,
        #     '\n\t',
        #     'Part::KVPairs=', part_kvpairs
        # )

        return packed_data

    # @staticmethod
    # @final
    # def unpack(data):
    #     offset = type_func.IndexOffset.Offset(data)
    #     this_length = type_func.bytes_to_int(offset >> length_bytes_settings['TypeName'])
    #     this_name = (offset >> this_length).decode()
    #     dct = {}
    #
    #     while not offset.isend():
    #         length_1, length_2, length_3 = (
    #             type_func.bytes_to_int(offset >> length_bytes_settings['AttrName']),
    #             type_func.bytes_to_int(offset >> length_bytes_settings['AttrValue']),
    #             type_func.bytes_to_int(offset >> length_bytes_settings['AttrType']),
    #         )
    #         name = (offset >> length_1).decode()
    #         packed_data = offset >> length_2
    #         type_name = (offset >> length_3).decode()
    #
    #         if type_name == 'BinStruct':
    #             origin_data = BinStruct.unpack(packed_data)
    #         else:
    #             origin_data = auto_struct.unpack(getattr(builtins, type_name), packed_data)
    #         dct[name] = origin_data
    #     typ = _get_class(this_name)
    #     print(typ, this_name)
    #     return typ(**dct)

    @final
    @staticmethod
    def unpack(data, *args, **kwargs):
        """
        解包结构体.
        :param data: 原始数据
        :param args: 传递给unpack_event函数的参数
        :param kwargs: 传递给unpack_event函数的参数
        """
        offset = type_func.IndexOffset.Offset(data)
        this_length = type_func.bytes_to_int(offset >> length_bytes_settings['TypeName'])
        this_name = (offset >> this_length).decode()

        typ = _get_class(this_name)

        bitmap_length = _get_attr_bitmap_length(len(typ.__data__))
        bitmap = type_func.Bitmap.unpack(offset >> bitmap_length)

        # 获取已设置的属性
        set_attrs = [attr_name for attr_name, on in zip(typ.__data__, bitmap) if on]
        # print(set_attrs)
        temp_dct = {}

        attr_count = 0
        while not offset.isend():
            length_1, length_2 = (
                type_func.bytes_to_int(offset >> length_bytes_settings['AttrValue']),
                type_func.bytes_to_int(offset >> length_bytes_settings['AttrType']),
            )
            packed_data = offset >> length_1
            type_name = (offset >> length_2).decode()
            if type_name in bin_types:
                origin_data = BinStruct.unpack(packed_data)
            else:
                origin_data = auto_struct.unpack(getattr(builtins, type_name), packed_data)

            temp_dct[attr_count] = origin_data
            attr_count += 1

        attr_dct = {}

        for attr, value in temp_dct.items():
            attr_dct[set_attrs[attr]] = value

        ins = typ(**attr_dct)  # type: BinStruct
        Res = ins.unpack_event(*args, **kwargs)
        if Res is not None:
            if type_func.is_errortype(Res):
                raise UnpackError('An error occurred during unpacking') from Res
        return ins

    @classmethod
    def to_struct(cls, obj, __data__=None):
        """
        根据传入的对象以及__data__列表,构建结构体
        """
        if isinstance(obj, BinStruct):
            if __data__ is None:
                return obj
            elif __data__ == obj.__data__:
                return obj
            else:
                raise GeneraterError('无法确定结构体需要包含的属性')
        if __data__ is None:
            if hasattr(obj, '_data_'):
                __data__ = getattr(obj, '_data_')

        if __data__ is None:
            raise GeneraterError('无法确定结构体需要包含的属性')

        ins = cls(**{name: getattr(obj, name) for name in __data__})
        return ins

    @property
    def __attrs_dict(self):
        dct = {}
        for name in self.__data__:
            dct[name] = getattr(self, name)
        return dct

    def __str__(self):
        kv_pairs = list(self.__attrs_dict.items())
        return f'{self.__class__.__name__}({", ".join((f"{name}={repr(value)}" for name, value in kv_pairs))})'

    __repr__ = __str__


class Struct(Abc.Serializer):
    struct = BinStruct

    def dumps(self, data: BinStruct):
        return data.pack()

    def loads(self, data):
        return self.struct.unpack(data)


bin_types = {
    'BinStruct',
}
