from src.hydrolib.type_func.Overload import *


@overload
def func(a: int, b: int):
    return a * b + b


@overload
def func(a: str, b: str):
    return a.join(b)


@overload
def func(a: str, b=None):
    return a * b


print(list(get_func_overloads(func)))

# 正确示范
print(func(1, 2))
print(func("1", "2"))
print(func("x", 10))

# Error
try:
    print(func('ladjf', None))
except OverloadRuntimeError as e:
    print(e)
