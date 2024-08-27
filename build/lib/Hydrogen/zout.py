import logging
import msvcrt
import sys
import time
from datetime import timedelta
from decimal import Decimal
from typing import Callable

from .typefunc.dict import AttrDict

zout_logger = logging.getLogger("SzQlib.zout")


def double(num, context=...):
    return Decimal(str(num), context=context)


def mapping(stream, in_min, in_max, out_min, out_max, rt_function: Callable = float):
    stream = double(stream)
    in_min, in_max, out_min, out_max = map(double, (in_min, in_max, out_min, out_max))
    zout_logger.debug(f"Mapping data {stream} from {in_min} {in_max} to {out_min} {out_max}")
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


def get_color_init():
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
    print(get_color_init(), end='', file=file, flush=flush)


class Cursor:
    def __init__(self, row=1, col=1):
        self.row = row
        self.col = col

    def flush(self):
        row, col = get_base_cursor()
        if row is None:
            raise RuntimeError("刷新坐标失败")
        self.row, self.col = row, col

    @property
    def line(self):
        return self.row

    @property
    def column(self):
        return self.col

    def move(self, row, col):
        self.row, self.col = row, col
        print(f"\033[{row};{col}H", end='')

    def up(self, row):
        self.row += row
        print(f"\033[{row}A", end='')

    def down(self, row):
        self.row -= row
        print(f"\033[{row}B", end='')

    def left(self, col):
        self.col -= col
        print(f"\033[{col}D", end='')

    def right(self, col):
        self.col += col
        print(f"\033[{col}C", end='')

    def clear_now_line(self):
        self.col = 1
        print("\033[2K", end='')

    def clear(self):
        print('\033[2J')
        self.move(1, 1)

    def print(self, *values, sep=' ', end='\n', file=None, flush=False):
        line_count = 0
        for value in values:
            str_val = str(value)
            line_count += str_val.count('\n')
            if '\r' in str_val:
                r_list = str_val.split('\r')
                value_str = list("")
                for x in r_list:
                    if not value_str:
                        value_str.extend(list(x))
                    else:
                        if len(value_str) >= len(x):
                            value_str[: len(x)] = list(x)
                        else:
                            value_str.clear()
                            value_str.extend(list(x))
                self.col = len(value_str)
        self.row += line_count
        print(*values, sep=sep, end=end, file=file, flush=flush)

    def to_local(self):
        return LocalCursor(self)

    def __str__(self):
        return f"Cursor: row={self.row} col={self.col}"


class LocalCursor(Cursor):
    def __init__(self, base_class: Cursor, row=1, col=1):
        super().__init__(row, col)
        self.local_row = 0
        self.local_col = 0
        self.base = base_class

    def move(self, row, col):
        self.local_row = row
        self.local_col = col

        row = self.base.row + row
        col = self.base.col + col

        super(LocalCursor, self).move(row, col)

    def up(self, row):
        self.local_row -= row
        super(LocalCursor, self).up(row)

    def down(self, row):
        self.local_row += row
        super(LocalCursor, self).down(row)

    def left(self, col):
        self.local_col -= col
        super(LocalCursor, self).left(col)

    def right(self, col):
        self.local_col += col
        super(LocalCursor, self).right(col)

    @property
    def line(self):
        return self.local_row

    @property
    def column(self):
        return self.local_col


def get_base_cursor():
    # 发送请求光标位置的 ANSI 转义序列
    sys.stdout.write("\033[6n")
    sys.stdout.flush()

    timeout = 3

    start_time = time.time()
    response = ""
    while time.time() - start_time < timeout:
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8')
            if char == 'R':
                break
            response += char
        time.sleep(0.01)  # 减少CPU占用
    # 解析响应以获取光标位置
    # \x1b[27;1
    if response.startswith("\033["):
        response = response.split('\033[')[1]
        response = response.split(';')
        response = tuple(map(int, response))
        if len(response) == 2:
            row, col = response
            return row, col
        return None, None
    return None, None


def get_cursor():
    row, col = get_base_cursor()
    if row is not None and col is not None:
        return Cursor(row, col)
    return Cursor(0, 0)


class ProgressBar:
    def __init__(
            self, name=None, current=None, total=None, line=1, cursor: LocalCursor | Cursor = get_cursor().to_local(),
            bar_length=20,
            full_char: str = '-', empty: str = ' ', format=None
    ):
        if cursor is None:
            raise ValueError("cursor must be set")

        if current is None:
            current = 0

        if format is None:
            format = "{name} | {bar} eta {eta} {speed}"

        if total is None:
            raise ValueError("total must be set")
        self.name = name
        self.bar = ''
        self.eta = ''
        self.speed = None
        self.current = current
        self.total = total
        self.max_length = bar_length
        self.full_char = full_char
        self.empty = empty
        self.format = format
        self.cursor = cursor
        self.line = line
        self.start_time = None
        self.end_time = None

    def get_dict(self):
        return {
            'name': self.name,
            'bar': self.bar,
            'eta': self.eta,
            'speed': self.speed,
            'current': self.current,
            'total': self.total,
            'max_length': self.max_length,
            'full_char': self.full_char,
            'empty': self.empty,
            'format': self.format,
            'cursor': self.cursor,
            'line': self.line,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

    def _update_bar(self):
        """Calculate and display the progress bar."""
        percentage = self.current / self.total
        filled_length = int(self.max_length * percentage)
        bar = self.full_char * filled_length + self.empty * (self.max_length - filled_length)

        elapsed_time = time.time() - self.start_time
        eta = self._calculate_eta(percentage, elapsed_time)

        self.bar = bar
        self.eta = str(timedelta(seconds=int(eta)))
        self.speed = f"{self.current / elapsed_time if elapsed_time > 0 else 0:.2f}/s"

        self._render()

    def _calculate_eta(self, percentage, elapsed_time):
        """Calculate estimated time of arrival."""
        if percentage == 0:
            return 0
        eta = (elapsed_time / percentage) * (1 - percentage)
        return eta

    def _render(self):
        """Render the progress bar to the console."""
        self.cursor.move(self.line, 1)
        self.cursor.clear_now_line()
        self.cursor.print(self.format.format(**self.get_dict()), end='')
        self.cursor.move(self.line, 1)

    def update(self, current):
        """Update the progress."""
        self.current = current
        self._update_bar()

    def add(self, current):
        self.update(self.current + current)

    def finish(self):
        """Mark the progress as finished."""
        self.update(self.total)
        self.end_time = time.time()
        self.cursor.move(self.line, 0)
        self.cursor.clear_now_line()
        self.cursor.print()


class MultiProgressBar:
    def __init__(self):
        self.progress_bars = {}  # type: dict[object, ProgressBar]

    def add_bar(self, progress_bar: ProgressBar):
        name = progress_bar.name
        self.progress_bars[name] = progress_bar

    def update(self, name, current):
        self.progress_bars[name].update(current)

    def add(self, name, current):
        self.progress_bars[name].add(current)

    def finish(self, name):
        self.progress_bars[name].finish()

    def finish_all(self):
        for bars in self.progress_bars.values():
            bars.finish()




