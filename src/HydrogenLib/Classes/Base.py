from src.HydrogenLib.Decorators import singleton_decorator


class Char(int):
    def __init__(self, value=None):
        if value is None:
            self.value = 0
        elif isinstance(value, int):
            self.value = value
        elif isinstance(value, str):
            self.value = int.from_bytes(value.encode(errors='ignore'))

    def __str__(self):
        return chr(self.value)

    def __add__(self, other):
        if isinstance(other, int):
            return Char(self.value + other)
        elif isinstance(other, Char):
            return Char(self.value + other.value)
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Char' and '{type(other)}'")

    def __sub__(self, other):
        if isinstance(other, int):
            return Char(self.value - other)
        elif isinstance(other, Char):
            return Char(self.value - other.value)
        else:
            raise TypeError(f"unsupported operand type(s) for -: 'Char' and '{type(other)}'")


@singleton_decorator
class _Null:
    ...


@singleton_decorator
class _ObjectFunc:
    def setattr(self, __self, __key, __value):
        object.__setattr__(__self, __key, __value)

    def getattr(self, __self, __value):
        return object.__getattribute__(__self, __value)

    def delattr(self, __self, __value):
        object.__delattr__(__self, __value)

    def delself(self, __self):
        ds = []
        for i in globals():
            if i is __self:
                ds.append(i)
        for i in ds:
            globals().pop(i)


null = _Null()
ObjectFunc = _ObjectFunc()
INF = float('inf')
