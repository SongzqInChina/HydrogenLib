import msvcrt
import sys
import time
import traceback
from typing import Callable, Any

import qzlib

liblib = qzlib


class TestFunction:
    def __init__(self, func, activate):
        self.func = func
        self.activate = activate

    def __call__(self, *args, **kwargs):
        yield self.activate
        yield None
        yield self.func(*args, **kwargs)


def test_function(activate: Any = True) -> Callable[[Callable], TestFunction]:
    activate = bool(activate)

    def test_wrapper(func) -> TestFunction:
        return TestFunction(func, activate)

    return test_wrapper


def run_test(test_object: TestFunction):
    try:
        x = test_object()
        if next(x):
            next(x)
            end_string = next(x)
            return True, end_string
        return False, False
    except Exception as e:
        return False, e


def activate(func: TestFunction):
    func.activate = activate


def deactivate(func: TestFunction):
    func.activate = False


def test_main(__functions: list[TestFunction]):
    for func in __functions:
        print('-' * 40)
        print("Func:", func.func.__name__)
        if not isinstance(func, TestFunction):
            print("Error test function.")
        else:
            result, end = run_test(func)
            if result is True:
                print("Test Successful.")
                print("End String:", end)
            else:
                traceback.print_exception(end)

        print('\n' + '-' * 40)

