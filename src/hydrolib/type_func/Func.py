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


def is_instance(ins_or_cls):
    return not isinstance(ins_or_cls, type)


def get_qualname(func_type_or_ins: typing.Union[types.FunctionType, type, object]):
    if is_instance(func_type_or_ins) and not is_function(func_type_or_ins):
        return get_qualname(func_type_or_ins.__class__)
    return f'{func_type_or_ins.__module__}.{func_type_or_ins.__qualname__}'


def is_function(obj):
    Func_Callable_Types = typing.Union[types.FunctionType, types.BuiltinFunctionType]
    return isinstance(obj, Func_Callable_Types)
