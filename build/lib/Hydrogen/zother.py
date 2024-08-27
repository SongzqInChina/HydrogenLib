import inspect
import logging

# module end

zother_logger = logging.getLogger(__name__)


class cglobalc:
    _init = False

    def __init__(self, error='N/A', **kwargs):
        self._namesp = {}
        self._namesp = kwargs
        self.error = error
        self._init = True

    def set(self, key, value):
        self._namesp[key] = value

    def get(self, item):
        if item in self._namesp:
            return self._namesp[item]
        else:
            return self.error

    def __getattr__(self, item):
        if item in self._namesp:
            return self._namesp[item]
        else:
            return self.error

    def delt(self, item):
        if item in self._namesp:
            self._namesp.pop(item)

    def set_namespace(self, nsp: dict):
        self._namesp = nsp

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delt(key)

    def __getitem__(self, item):
        return self.get(item)

    def items(self):
        return self._namesp.items()

    def keys(self):
        return self._namesp.keys()

    def values(self):
        return self._namesp.values()


class globalc(cglobalc):
    def __init__(self, error="N/A", **kwargs):
        super().__init__(error, **kwargs)


class FobjectEx:
    def setattr(self, __self, __value):
        object.__setattr__(__self, __value)

    def getattr(self, __self, __value):
        return object.__getattribute__(__self, __value)

    def delattr(self, __self, __value):
        object.__delattr__(__self, __value)

    def delself(self, __self, globals=globals()):
        ds = []
        for i in globals:
            if i is __self:
                ds.append(i)
        for i in ds:
            globals.pop(i)


Fobject = FobjectEx()


def get_all_arguments(func):
    argspec = inspect.getfullargspec(func)
    return argspec.args


class StructEx:
    def __init__(self, _self, **kwargs):
        self.__data__ = {}
        self.__data__.update(**kwargs)

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        try:
            return self.__dict__.get(item)
        except KeyError:
            return self.__data__.get(item)

    def __setattr__(self, key, value):
        if self.__data__ is not None and key not in self.__data__:
            self.__data__[key] = value
        else:
            self.__dict__[key] = value


class Struct(StructEx):

    def __str__(self):
        string = ""

        for i in self.__data__:
            if i == "__data__":
                continue
            string += f"{i}={self.__data__[i]}, "

        string = string[:-2]

        return f"{self.__module__}.{self.__class__.__name__}({string})"

    __repr__ = __str__


def default_function(*args, **kwargs):
    def wrap(func):
        def wrapper():
            return func(*args, **kwargs)

        return wrapper

    return wrap


def struct(**kwargs):
    def decorator(cls):
        class GettingClass:
            def __call__(self, **kwargs_x):
                kwargs.update(kwargs_x)

                class wrap(cls, Struct):
                    ...

                return wrap(cls, **kwargs_x)

            def __repr__(self):
                return str(Struct)

            __str__ = __repr__

        instance = GettingClass()
        return instance.__call__

    return decorator


def singleton_decorator(classic):
    zother_logger.debug(f"""Create property object '{classic.__name__}'""")

    class wrap(classic):
        _Instance = None

        def __new__(cls, *args, **kwargs):
            if wrap._Instance is None:
                wrap._Instance = super().__new__(cls, *args, **kwargs)
            return wrap._Instance

    return wrap


@singleton_decorator
class null_t:
    ...


INF = float('inf')

null = null_t()

zother_logger.debug("Module zother loading ...")
