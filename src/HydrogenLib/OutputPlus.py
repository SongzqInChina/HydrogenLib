import logging
import sys
import time
from datetime import timedelta
from decimal import Decimal
from typing import Callable

outputplus_logger = logging.getLogger("HydrogenLib.OutputPlus")


def double(num, context=...):
    return Decimal(str(num), context=context)


def mapping(stream, in_min, in_max, out_min, out_max, rt_function: Callable = float):
    stream = double(stream)
    in_min, in_max, out_min, out_max = map(double, (in_min, in_max, out_min, out_max))
    outputplus_logger.debug(f"Mapping data {stream} from {in_min} {in_max} to {out_min} {out_max}")
    return rt_function(out_min + (in_max - in_min) * (stream - in_min) / (out_max - out_min))


def get_foreground(r, g, b):
    if not any((r, g, b)):
        return ''  # 不需要定义颜色
    return f"\033[38;2;{r};{g};{b}m"


def get_background(r, g, b):
    if not any((r, g, b)):
        return ''  # 不需要定义颜色
    return f"\033[48;2;{r};{g};{b}m"


def get_color_head(fr_r=0, fr_g=0, fr_b=0, bk_r=0, bk_g=0, bk_b=0):
    return get_foreground(fr_r, fr_g, fr_b) + get_background(bk_r, bk_g, bk_b)


def color_init():
    return "\033[0m"


def print_color(
        *values, sep=' ', end='\n',
        file=None, flush=False,
        foreground=None, background=None
):
    """
    :param values:
    :param sep:
    :param end:
    :param file:
    :param flush:
    :param foreground: 这个参数的实参应为一个iterable，所有值为int或其子类
    :param background: 这个参数的实参应为一个iterable，所有值为int或其子类
    :return: None
    """
    if not background:
        background = (0, 0, 0)
    if not foreground:
        foreground = (0, 0, 0)

    foreground = tuple(map(int, foreground))
    background = tuple(map(int, background))

    foreground += (0, 0, 0)

    background += (0, 0, 0)

    r, g, b = foreground[:3:]
    print(get_foreground(r, g, b), end='', file=file, flush=flush)
    r, g, b = background[:3:]
    print(get_background(r, g, b), end='', file=file, flush=flush)
    print(*values, sep=sep, end=end, file=file, flush=flush)
    print(color_init(), end='', file=file, flush=flush)


class RedirectOutput:
    """
    重定向输出或输入至/来自IO对象或文件标识符
    例如：
    ```
        stdout, stderr = io.StringIO(), io.StringIO()
        with RedirectOutput(stdout, stderr):
            # 执行你想要执行的语句
            ...
        print(stdout.getValue(), stderr.getValue())
    ```
    """

    def __init__(self, stdout=..., stderr=..., stdin=...):
        if stdout is ...:
            stdout = sys.stdout
        if stderr is ...:
            stderr = sys.stderr
        if stdin is ...:
            stdin = sys.stdin
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin

    def redirect(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        sys.stdin = self.stdin

    def unredirect(self):
        sys.stdout, sys.stderr, sys.stdin = sys.__stdout__, sys.__stderr__, sys.__stdin__

    def __enter__(self):
        self.redirect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unredirect()
