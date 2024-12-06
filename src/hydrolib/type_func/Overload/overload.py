from collections import deque
from fractions import Fraction
from inspect import signature, Signature

import rich

from ..Func import *
from ...data_structures import Heap

overloads = {}  # type: dict[str, Heap]
overload_temp = {}  # type: dict[str, dict[tuple[type, ...], OverloadFunctionCallable]]
overload_funcs = {}  # type: dict[str, OverloadFunctionCallable]


# TODO: 完成模块

def _register(qual_name, func: 'OverloadFunction'):
    if qual_name not in overload_funcs:
        overload_funcs[qual_name] = OverloadFunctionCallable(qual_name)
    return _get_registered(qual_name)


def _get_registered(qual_name):
    return overload_funcs[qual_name]


def _add_to_temp(qual_name, types):
    if qual_name not in overload_temp:
        overload_temp[qual_name] = dict()
    overload_temp[qual_name][types] = _get_registered(qual_name)


def _check_temp(qual_name, args):
    if qual_name not in overload_temp:
        return False
    for types in overload_temp[qual_name]:
        if len(types) != len(args):
            continue
        for arg, type_ in zip(args, types):
            if not isinstance(arg, type_):
                return False


class FalseError:
    def __init__(self, exc):
        self.exception = exc

    def __bool__(self):
        return False

    def __str__(self):
        return str(self.exception)

    __repr__ = __str__


class OverloadError(Exception):
    def __init__(self, qual_name, tests=(), args=(), kwargs=None):
        self.qual_name = qual_name
        self.tests = tests
        self.msg = ''
        self.args = args
        self.kwargs = kwargs if kwargs else {}

    @staticmethod
    def to_call_format(args, kwargs):
        string = ', '.join(
            list(map(lambda x: type(x).__name__, args)) +
            list(map(lambda x: f'{x[0]}={type(x[1]).__name__}', kwargs.items()))
        )
        return string

    @staticmethod
    def to_args_format(signature: Signature):
        params = signature.parameters
        string = ', '.join(
            list(map(str, params.values()))
        )
        return string

    @staticmethod
    def to_type_name(type_: inspect.Parameter):
        if type_.annotation is inspect.Parameter.empty:
            return 'Any'
        else:
            return str(type_.annotation.__name__)

    @classmethod
    def to_types_format(cls, signature: Signature):
        params = signature.parameters
        string = ', '.join(
            list(map(cls.to_type_name, params.values()))
        )
        return string

    @staticmethod
    def __rich_to_string(string):
        console = rich.get_console()
        rich_string = console.render(string)
        result = ''
        for part in rich_string:
            result += str(part.text)
        return result

    def __generate_error_msg(self):
        error_msg = ''

        def add_error_msg(string):
            nonlocal error_msg
            error_msg += self.__rich_to_string(string)

        add_error_msg(f'[red]调用{self.qual_name}时发生错误: 无法匹配重载类型[/red]')
        add_error_msg(f'[yellow]传入的实参:[/yellow] {self.to_call_format(self.args, self.kwargs)}')
        for test, func in zip(self.tests, overloads[self.qual_name]):
            add_error_msg(
                f'\t[yellow]尝试匹配: ({self.to_types_format(func.signature)}) [/yellow]'
                f'[red]: {str(test)}[/red]'
            )
        return error_msg

    def __str__(self):
        return self.__generate_error_msg()


class OverloadRuntimeError(Exception):
    def __init__(self, qual_name, called_overload, e, call_args, call_kwargs):
        self.qual_name = qual_name
        self.called_overload = called_overload
        self.e = e
        self.call_args = call_args
        self.call_kwargs = call_kwargs

    def __str__(self):
        return f'以参数({OverloadError.to_call_format(self.call_args, self.call_kwargs)})调用`{self.qual_name}`的重载 "{self.called_overload}" 时发生错误:{self.e.__class__.__name__}'


class OverloadFunction:
    def __init__(self, func):
        self.func = func
        self.qual_name = get_qualname(func)
        self.signature = signature(func)
        self.prec = self.get_prec(self.signature)
        print("重载精确度:", self.prec)

    @staticmethod
    def get_prec(signature: Signature):
        return Fraction(
            sum(
                map(
                    lambda x: x.annotation is not inspect.Parameter.empty,
                    signature.parameters.values()
                )
            ),
            len(signature.parameters)
        )

    def __lt__(self, other):
        return self.prec < other.prec

    def __eq__(self, other):
        return self.prec == other.prec

    def __gt__(self, other):
        return self.prec > other.prec

    def __str__(self):
        return f'Overload({self.signature}) with prec {self.prec}'

    __repr__ = __str__


class OverloadFunctionCallable:
    def __init__(self, qual_name):
        self.qual_name = qual_name

    def __is_match_type(self, func: OverloadFunction, args: inspect.BoundArguments):
        def raise_(param, except_type, real_type):
            return FalseError(TypeError(
                f'参数`{param.name}`类型错误, 期望`{except_type.__name__}`, 实际为`{real_type.__name__}`'
            ))

        for param in func.signature.parameters.values():
            if param.annotation is inspect.Parameter.empty:
                continue
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                for arg in args.args:
                    if not isinstance(arg, param.annotation):
                        return raise_(param, param.annotation, arg.__class__)
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                for arg in args.kwargs.values():
                    if not isinstance(arg, param.annotation):
                        return raise_(param, param.annotation, arg.__class__)
            else:
                except_type = param.annotation
                real_type = args.arguments[param.name].__class__
                if not issubclass(real_type, except_type):
                    return raise_(param, except_type, real_type)
        return True

    def __can_call_with_param(self, func: OverloadFunction, *args, **kwargs):
        try:
            args = func.signature.bind(*args, **kwargs)
            return self.__is_match_type(func, args)
        except TypeError as e:
            return FalseError(e)

    def test_with_args(self, *args, **kwargs):
        for func in overloads[self.qual_name]:
            test_res = self.__can_call_with_param(func, *args, **kwargs)
            if test_res:
                return True
        return False

    def __call__(self, *args, **kwargs):
        if _check_temp(self.qual_name, args, kwargs):
            return
        test_results = deque()
        for func in overloads[self.qual_name]:

            test_res = self.__can_call_with_param(func, *args, **kwargs)
            test_results.append(test_res)

            if test_res:
                try:
                    return func.func(*args, **kwargs)
                except Exception as e:
                    raise OverloadRuntimeError(self.qual_name, func.signature, e, args, kwargs)

        raise OverloadError(
            self.qual_name, tuple(test_results), args, kwargs
        )


def overload(func):
    func = OverloadFunction(func)
    if func.qual_name in overloads:
        overloads[func.qual_name].append(func)
    else:
        overloads[func.qual_name] = Heap([func], True)

    return _register(func.qual_name, func)


def get_func_overloads(func: OverloadFunctionCallable):
    return overloads[func.qual_name]
