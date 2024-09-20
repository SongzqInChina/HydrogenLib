import curses
import rich
import rich.panel
import rich.table
from rich import print

from ._base import InteractiveCLI
from ..DataStructures import Stack


class Options:
    def __init__(self, name: str, options):
        self.name = name
        self.options = options

    def get(self, index):
        return self.options[index]

    def is_submenu(self, index):
        return isinstance(self.options[index], self.__class__)

    def get_submenus(self):
        return [(i, v) for i, v in enumerate(self.options) if self.is_submenu(i)]

    def get_submenu(self, index):
        if not self.is_submenu(index):
            raise ValueError("Not a submenu")
        return self.options[index]

    def get_options(self):
        return [(i, v) for i, v in enumerate(self.options) if not self.is_submenu(i)]

    def __len__(self):
        return len(self.options)


class Menu(InteractiveCLI):
    def __init__(self, name: str, options: Options, default: int = 0, callback=None):
        self.name = name
        self.options = options
        self.select_pair = default
        self.unselected_pair = default + 1
        self.callback = callback
        self.exit_text = "Exit"

    def _curses_menu(self, stdscr):
        curses.initscr()
        curses.start_color()
        pair1 = curses.color_pair(self.select_pair)
        pair2 = curses.color_pair(self.unselected_pair)

        opt_stack = Stack()
        rows_stack = Stack()
        opt_stack.push(self.options)
        rows_stack.push(0)
        while True:
            stdscr.clear()
            table = rich.table.Table("Options", "Description")
            cur_opt = opt_stack.front
            cur_row = rows_stack.front

            # Display options with highlighting
            for i, v in cur_opt.get_options():
                style = f"{pair1 if i == cur_row else pair2}"
                table.add_row(
                    rich.panel.Panel(
                        v.name,
                        title=f"[bold]{i}[/bold]",
                        expand=False,
                        style=style,
                    ),
                    v.description,
                )
            table.add_row(
                rich.panel.Panel(
                    self.exit_text,
                    title=f"[bold]{len(cur_opt) - 1}[/bold]",
                    expand=False,
                    style=f"{pair1 if len(cur_opt) - 1 == cur_row else pair2}",
                )
            )

            stdscr.addstr(str(table))

            ch = stdscr.getch()
            if ch == curses.KEY_UP:
                new_row = max(0, cur_row - 1)
                rows_stack.pop()
                rows_stack.push(new_row)
                cur_row = rows_stack.front
            elif ch == curses.KEY_DOWN:
                new_row = min(len(cur_opt) - 1, cur_row + 1)
                rows_stack.pop()
                rows_stack.push(new_row)
                cur_row = rows_stack.front
            elif ch == curses.KEY_ENTER:
                if cur_opt.is_submenu(cur_row):
                    opt_stack.push(cur_opt.get_submenu(cur_row))
                    rows_stack.push(0)
                else:
                    rt_value = self.callback(opt_stack, cur_opt, cur_row)
                    if rt_value == 1:  # 结束菜单信号
                        return

    def __enter__(self):
        print(f"[bold]{self.name}[/bold]")
        curses.wrapper(self._curses_menu)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
