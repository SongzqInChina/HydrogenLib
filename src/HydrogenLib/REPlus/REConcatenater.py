import re

from . import _reconcatenater_abc as _abc

both_set_activate = 0


# 0 raise error
# 1 name only
# 2 ignore only


class REConcater(_abc.REConcater):

    def __init__(self, pattern: _abc.BaseREConcateratable | str):
        if isinstance(pattern, _abc.BaseREConcateratable):
            self._cur_pattern = pattern
        elif isinstance(pattern, str):
            self._cur_pattern = REConcateratable(pattern)
        else:
            raise TypeError("pattern must be str or BaseREConcateratable")

    @classmethod
    def concat(cls, *args: _abc.BaseREConcateratable):
        return cls(''.join(
            map(lambda x: str(x.pattern()), args)
        ))

    @classmethod
    def or_(cls, *args: _abc.BaseREConcateratable):
        return cls('|'.join(
            map(lambda x: x.pattern(), args)
        ))

    def pattern(self):
        return self._cur_pattern.pattern()

    def match(self, string):
        return self._cur_pattern.match(string)

    def findall(self, string):
        return self._cur_pattern.findall(string)

    def finditer(self, string):
        return self._cur_pattern.finditer(string)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            other = other._cur_pattern
        return self.concat(self._cur_pattern, other)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("can only multiply by int")
        return self.concat(*(self for _ in range(other)))

    def __or__(self, other):
        return self.or_(self._cur_pattern, other)

    def __str__(self):
        return self.pattern()


class BaseREConcateratable(_abc.BaseREConcateratable):
    """
    RE组合基类
    - name 为组命名
    - ignore 是否选择出现在结果列表(groups函数)中，往往出现在需要判断却不需要获取结果的文本部分
    - _pattern 原始文本/RE表达式
    """
    name = None
    ignore = False
    origin_pattern = None

    def pattern(self):

        ignore, name, pattern = self.ignore, self.name, self.origin()  # 提取变量

        if ignore is not False and name is not None:  # ignore=True, name=Any
            if both_set_activate == 0:
                raise NotImplementedError("ignore and name cannot be both set")
            elif both_set_activate == 1:
                ignore = False  # 取消忽略标记
            elif both_set_activate == 2:
                name = None  # 取消命名标记

        if name is not None:  # ignore=False, name=Any
            return "(?P<{name}>{pattern})".format(name=name, pattern=pattern)
        if ignore:  # ignore=True, name=None
            return "(?:{pattern})".format(pattern=pattern)
        else:
            return f"{pattern}"

    def origin(self):
        if isinstance(self.origin_pattern, str):
            return self.origin_pattern
        self.origin_pattern = self.origin_pattern.origin()
        return self.origin()

    def match(self, string):
        return re.match(self.pattern(), string)

    def findall(self, string):
        return re.findall(self.pattern(), string)

    def finditer(self, string):
        return re.finditer(self.pattern(), string)


class REConcateratable(BaseREConcateratable):
    def __init__(self, pattern, name=None, ignore=False):
        if isinstance(pattern, self.__class__):
            self.origin_pattern = pattern.origin()
        self.origin_pattern = pattern
        self.name, self.ignore = name, ignore

    def __add__(self, other):
        return REConcater(self) + other

    def __mul__(self, other):
        return REConcater(self) * other

    def __or__(self, other):
        return REConcater(self) | other

    def __str__(self):
        return self.pattern()


class Re(REConcateratable):
    ...


class Literal(REConcateratable):
    def __init__(self, pattern, name=None, ignore=False):
        super().__init__(
            re.escape(pattern), name, ignore
        )
