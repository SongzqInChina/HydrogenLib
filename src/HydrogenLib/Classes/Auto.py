from copy import deepcopy


class AutoCreateDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_value = None

    def __missing__(self, key):
        self[key] = deepcopy(self.default_value)
        return self[key]


class AutoCompareClass:
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

        if not isinstance(other, AutoCompareClass):
            if self._compare_attrs:
                value = getattr(self, self._compare_attrs[0])
                return func(value, other)

        if self._compare_attrs is None or other._compare_attrs is None:
            return defautl

        my_attr_values = (
            getattr(self, attr) for attr in self._compare_attrs
        )
        other_attr_values = (
            getattr(other, attr) for attr in other._compare_attrs
        )
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


class AutoJsonPickler:
    _pickle_attrs = None

    def __getstate__(self):
        if self._pickle_attrs is None:
            return self.__dict__
        return {attr: getattr(self, attr) for attr in self._pickle_attrs}

    def __setstate__(self, state):
        if self._pickle_attrs is None:
            self.__dict__ = state
        else:
            for attr in self._pickle_attrs:
                setattr(self, attr, state[attr])
