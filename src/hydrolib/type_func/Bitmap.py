from typing import Iterable


class Bitmap:
    def __init__(self, bits=None):
        if bits is None:
            self.num = 0
        elif isinstance(bits, int):
            self.num = bits
        elif isinstance(bits, Iterable):
            self.num = int(''.join(map(str, bits)), 2)

    def get_bit(self, index):
        return bool(self.num & (1 << index))

    def set_bit(self, index, on=1):
        if on:
            self.num |= (1 << index)
        else:
            self.num &= ~(1 << index)

    def pack(self):
        from . import int_to_bytes_nonelength
        return int_to_bytes_nonelength(self.num)

    @classmethod
    def unpack(cls, data):
        from . import bytes_to_int
        num = bytes_to_int(data)
        return cls(num)

    def __iter__(self):
        return iter(map(lambda x:bool(int(x)), bin(self.num)[2:]))

    def __str__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}({bin(self.num)})"

    __repr__ = __str__
