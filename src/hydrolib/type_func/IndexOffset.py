from abc import abstractmethod
from typing import Any, Callable


class OffsetFunction:
    @abstractmethod
    def offset(self, fat, lenght): ...

    @abstractmethod
    def n_offset(self, fat, lenght): ...

    @abstractmethod
    def back(self, fat, lenght): ...

    @abstractmethod
    def n_back(self, fat, lenght): ...

    @abstractmethod
    def offseter(self, fat, lenght): ...

    @abstractmethod
    def backer(self, fat, lenght): ...

    @abstractmethod
    def isend(self, fat): ...

    @abstractmethod
    def isstart(self, fat): ...

    @abstractmethod
    def n_offseter(self, fat, lenght): ...

    @abstractmethod
    def n_backer(self, fat, lenght): ...

    @abstractmethod
    def add_start(self, fat, lenght): ...

    @abstractmethod
    def less_start(self, fat, lenght): ...

    @abstractmethod
    def get_add_start(self, fat, lenght): ...

    @abstractmethod
    def get_less_start(self, fat, lenght): ...

    @abstractmethod
    def init_start(self, fat): ...

    @abstractmethod
    def get_start_less(self, fat, other): ...


class IterableOffsetFunction(OffsetFunction):
    def init_start(self, fat):
        fat.start = 0

    def less_start(self, fat, lenght):
        fat.start -= lenght

    def add_start(self, fat, lenght):
        fat.start += lenght

    def get_add_start(self, fat, lenght):
        return fat.start + lenght

    def get_less_start(self, fat, lenght):
        return fat.start - lenght

    def get_start_less(self, fat, other):
        return other - fat.start

    def offset(self, fat, lenght):
        # print(fat.start, lenght)
        if fat.start + lenght > len(fat.iterable):
            raise RuntimeError("Cannot offset {} lenghts (only {}).".format(lenght, len(fat.iterable) - fat.start))
        data = fat.iterable[fat.start: self.get_add_start(fat, lenght)]
        self.add_start(fat, lenght)
        if isinstance(data, tuple):
            return data[0]
        return data

    def n_offset(self, fat, lenght):
        data = fat.iterable[fat.start: self.get_add_start(fat, lenght)]
        return data

    def back(self, fat, lenght):
        if fat.start < lenght:
            raise ValueError("Cannot back {} lenghts (only {}).".format(lenght, fat.start))
        data = fat.iterable[self.get_less_start(fat, lenght): fat.start]
        self.less_start(fat, lenght)
        return data

    def n_back(self, fat, lenght):
        data = fat.iterable[self.get_less_start(fat, lenght): fat.start]
        return data

    def offseter(self, fat, lenght):
        return fat.__class__(self.offset(fat, lenght), self)

    def backer(self, fat, lenght):
        return fat(self.back(fat, lenght), self)

    def isend(self, fat):
        return fat.start >= len(fat.iterable) - 1

    def isstart(self, fat):
        return fat.start <= 0

    def n_offseter(self, fat, lenght):
        return fat(self.n_offset(fat, lenght), self)

    def n_backer(self, fat, lenght):
        return fat(self.n_back(fat, lenght), self)


class Offset:
    offset_func: OffsetFunction

    offset = lambda self, lenght: self.offset_func.offset(self, lenght)
    n_offset = lambda self, lenght: self.offset_func.n_offset(self, lenght)
    back = lambda self, lenght: self.offset_func.back(self, lenght)
    n_back = lambda self, lenght: self.offset_func.n_back(self, lenght)
    add_start = lambda self, lenght: self.offset_func.add_start(self, lenght)
    less_start = lambda self, lenght: self.offset_func.less_start(self, lenght)
    offseter = lambda self, lenght: self.offset_func.offseter(self, lenght)
    backer = lambda self, lenght: self.offset_func.backer(self, lenght)
    n_offseter = lambda self, lenght: self.offset_func.n_offseter(self, lenght)
    n_backer = lambda self, lenght: self.offset_func.n_backer(self, lenght)
    isend = lambda self: self.offset_func.isend(self)
    isstart = lambda self: self.offset_func.isstart(self)

    def __init__(self, iterable, offset_func: OffsetFunction | None = None):
        if offset_func is None:
            offset_func = IterableOffsetFunction()
        self.iterable = iterable

        self.start = None

        self.offset_func = offset_func
        self.offset_func.init_start(self)

    def __iter__(self):
        return self.iterable[self.start:]

    def __getitem__(self, item):
        return self.iterable[item]

    def __len__(self):
        return len(self.iterable)

    def __setitem__(self, key, value):
        self.iterable[key] = value

    def to(self, _Type):
        try:
            return _Type(self.iterable)
        except TypeError as e:
            raise e from None
        except Exception as e:
            raise e from None

    def surplus(self, _Type: None | Callable = None):
        if _Type is None:
            return self.n_offset(self.offset_func.get_start_less(self, len(self)))
        else:
            return _Type(self.surplus())

    # >
    def __gt__(self, lenght) -> Any:
        """
        get_offset.get_offset(lenght)
        :param lenght: an int value of lenght
        :return: Iterable
        """
        return self.offset(lenght)

    # <
    def __lt__(self, lenght) -> Any:
        """
        get_offset.get_offset(lenght)
        :param lenght: an int value of lenght
        :return: Iterable
        """
        return self.back(lenght)

    # >=
    def __ge__(self, lenght) -> Any:
        """
        get_offset.n_offset(lenght)
        :param lenght: an int value of lenght
        :return: Iterable
        """
        return self.n_offset(lenght)

    # <=
    def __le__(self, lenght) -> Any:
        """
        get_offset.get_offset(lenght)
        :param lenght: an int value of lenght
        :return: Iterable
        """
        return self.n_back(lenght)

    # +
    def __add__(self, lenght) -> Any:
        """
        start += lenght
        :param lenght: an int value of lenght 
        :return: None
        """
        self.add_start(lenght)

    # -
    def __sub__(self, lenght) -> Any:
        """
        start -= lenght
        :param lenght: an int value of lenght
        :return: None
        """
        self.less_start(lenght)

    # +=
    def __iadd__(self, lenght) -> Any:
        """
        start += lenght
        :param lenght: an int value of lenght
        :return: None
        """
        self.add_start(lenght)
        return self

    # -=
    def __isub__(self, lenght) -> Any:
        """
        start -= lenght
        :param lenght: an int value of lenght
        :return: None
        """
        self.less_start(lenght)
        return self

    def __lshift__(self, other):
        return self.back(other)

    def __rshift__(self, other):
        return self.offset(other)
