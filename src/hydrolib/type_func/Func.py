import inspect
import types
import typing


def get_args(func):
    for i in inspect.signature(func).parameters.values():
        yield i.name, i.default, i.kind, i.annotation


def get_name(func):
    return func.__name__


def get_doc(func):
    return func.__doc__


def get_code(func):
    return func.__code__


def get_source(func):
    return inspect.getsource(func)


def get_module(func):
    return func.__module__


def get_qualname(func):
    return f'{func.__module__}.{func.__qualname__}'


def is_function(obj):
    Func_Callable_Types = typing.Union[types.FunctionType, types.BuiltinFunctionType]
    return isinstance(obj, Func_Callable_Types)


