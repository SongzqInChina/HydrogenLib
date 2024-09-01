import inspect
import logging

# module end

zother_logger = logging.getLogger(__name__)


class Namespace:
    _init = False

    def __init__(self, error='N/A', **kwargs):
        self._namesp = kwargs
        self.error = error

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


class globalc(Namespace):
    def __init__(self, error="N/A", **kwargs):
        super().__init__(error, **kwargs)


class ObjectFunc_t:
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


ObjectFunc = ObjectFunc_t()


def get_all_arguments(func):
    argspec = inspect.getfullargspec(func)
    return argspec.args


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
