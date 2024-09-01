from Hydrogen.Decorators import singleton_decorator


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


ObjectFunc = _ObjectFunc()
