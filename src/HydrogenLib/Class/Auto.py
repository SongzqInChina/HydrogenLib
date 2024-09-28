from abc import ABC
from copy import deepcopy
from types import FunctionType

from src.HydrogenLib.TypeFunc import get_attr_by_path
from .Namespace import Namespace


class Auto(ABC):
    pass


class AutoRegDict(Auto):
    """
    自动注册未存在于字典的键，同时访问时返回默认值

    可以通过指定`isdeepcopy`属性来说明是否对默认值进行copy操作
    """
    default_value = None
    isdeepcopy = True

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def pop(self, key):
        return self._dict.pop(key)

    def copy(self):
        return self._dict.copy()

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def clear(self):
        return self._dict.clear()

    def __contains__(self, key):
        return self._dict.__contains__(key)

    def __len__(self):
        return self._dict.__len__()

    def __getitem__(self, key):
        if key not in self._dict:
            if self.isdeepcopy:
                v = deepcopy(self.default_value)
            else:
                v = self.default_value
            self._dict[key] = v
            return v
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]


class AutoCompare(Auto):
    """
    自动完成比较操作
    通过指定`_compare_attrs`属性来指定比较的属性，默认为None，
    如果`_compare_attrs`为None，那么自动比较将不会生效，而是根据比较符返回一个默认值
    如果被比较的对象不是 `AutoCompare` 的实例，那么比较时会按比较列表的第一个属性作为比较属性
    """
    _compare_attrs = None
    _cmp_funcs = {
        'eq': lambda x, y: x == y,
        'ne': lambda x, y: x != y,
        'lt': lambda x, y: x < y,
        'gt': lambda x, y: x > y,
        'le': lambda x, y: x <= y,
        'ge': lambda x, y: x >= y
    }

    def _auto_compare_attrs(self, opt, other, defautl=False):
        if opt not in self._cmp_funcs:
            return defautl

        func = self._cmp_funcs[opt]

        if not isinstance(other, AutoCompare):
            if self._compare_attrs:
                value = getattr(self, self._compare_attrs[0])
                return func(value, other)

        if self._compare_attrs is None or other._compare_attrs is None:
            return defautl

        my_attr_values = (
            getattr(self, attr) for attr in self._compare_attrs)
        other_attr_values = (
            getattr(other, attr) for attr in other._compare_attrs)
        return func(my_attr_values, other_attr_values)

    def __eq__(self, other):
        return self._auto_compare_attrs('eq', other, False)

    def __ne__(self, other):
        return self._auto_compare_attrs('ne', other, True)

    def __lt__(self, other):
        return self._auto_compare_attrs('lt', other, False)

    def __gt__(self, other):
        return self._auto_compare_attrs('gt', other, False)

    def __le__(self, other):
        return self._auto_compare_attrs('le', other, True)

    def __ge__(self, other):
        return self._auto_compare_attrs('ge', other, True)


class AutoState(Auto):
    """
    自动完成对象的状态导出和恢复

    如果`_state_attrs`为None，那么将导出所有属性，恢复时同上
    """
    _state_attrs = None

    def __getstate__(self):
        if self._state_attrs is None:
            return self.__dict__
        return {attr: getattr(self, attr) for attr in self._state_attrs}

    def __setstate__(self, state):
        if self._state_attrs is None:
            self.__dict__ = state
        else:
            for attr in self._state_attrs:
                setattr(self, attr, state[attr])


class AutoOperator(Auto):
    _operator_funcs = {}

    def __add__(self, other):
        return self._operator_funcs['+'](self, other)

    def __sub__(self, other):
        return self._operator_funcs['-'](self, other)

    def __mul__(self, other):
        return self._operator_funcs['*'](self, other)

    def __truediv__(self, other):
        return self._operator_funcs['/'](self, other)

    def __floordiv__(self, other):
        return self._operator_funcs['//'](self, other)

    def __mod__(self, other):
        return self._operator_funcs['%'](self, other)

    def __pow__(self, other):
        return self._operator_funcs['**'](self, other)

    def __and__(self, other):
        return self._operator_funcs['&'](self, other)

    def __or__(self, other):
        return self._operator_funcs['|'](self, other)

    def __xor__(self, other):
        return self._operator_funcs['^'](self, other)

    def __lshift__(self, other):
        return self._operator_funcs['<<'](self, other)

    def __rshift__(self, other):
        return self._operator_funcs['>>'](self, other)

    def __invert__(self):
        return self._operator_funcs['~'](self)

    def __neg__(self):
        return self._operator_funcs['-'](self)


class AutoOperatorStruct:
    @classmethod
    def decorator(cls, oper, globs):
        def wrapper(func):
            return cls(oper, func, globs)

        return wrapper

    def __init__(self, oper: str, func: FunctionType, _globals=None):
        self.oper = oper
        self.func = func

        if oper not in {
            '+', '-', '*', '/', '//', '%', '**', '&', '|', '^', '<<', '>>'
        }:
            raise ValueError(f"{oper} is not a valid operator")

        cls = get_attr_by_path(Namespace(None, **_globals), func.__qualname__).lst[-2]
        if not isinstance(cls, AutoOperator):
            raise TypeError(f"{cls} is not a AutoOperator")

        cls._operator_funcs[oper] = self

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class AutoOperatorFunc(Auto):
    def __init__(self, globs):
        self._globs = globs

    def operator(self, oper):
        return AutoOperatorStruct.decorator(oper, self._globs)


class _AutoInfo(Auto):
    ...


class AutoRepr(_AutoInfo):
    _repr_attrs = None

    def __repr__(self):
        return str(
            {attr: getattr(self, attr) for attr in self._repr_attrs}
        )


class AutoStr(_AutoInfo):
    _str_attrs = None

    def __str__(self):
        return str(
            {attr: getattr(self, attr) for attr in self._str_attrs}
        )


class AutoInfo(AutoRepr, AutoStr):
    _info_attrs = None

    def __repr__(self):
        self._repr_attrs = self._info_attrs
        return super().__repr__()

    def __str__(self):
        self._str_attrs = self._info_attrs
        return super().__str__()
