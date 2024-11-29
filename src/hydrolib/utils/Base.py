from ..decorators import singleton_decorator


class Char(int):

    def __str__(self):
        return chr(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({super().__repr__()})"


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
