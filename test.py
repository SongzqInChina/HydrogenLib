import curses


def draw_menu(stdscr, options, callback, select_fg=..., select_bg=..., unselect_fg=..., unselect_bg=...):
    if select_fg is ...:
        select_fg = curses.COLOR_BLACK
    if select_bg is ...:
        select_bg = curses.COLOR_WHITE
    if unselect_fg is ...:
        unselect_fg = curses.COLOR_WHITE
    if unselect_bg is ...:
        unselect_bg = curses.COLOR_BLACK

    # 初始化 curses
    curses.curs_set(0)  # 隐藏光标
    current_row = 0
    menu_options = list(options)

    # 设置颜色对
    curses.start_color()
    curses.init_pair(1, unselect_fg, unselect_bg)
    curses.init_pair(2, select_fg, select_bg)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # 绘制菜单项
        for idx, row in enumerate(menu_options):
            x = w // 2 - len(row) // 2
            y = h // 2 - len(menu_options) // 2 + idx
            if idx == current_row:
                stdscr.addstr(y, x, f"{idx + 1}. {row}", curses.color_pair(2))
            else:
                stdscr.addstr(y, x, f"{idx + 1}. {row}", curses.color_pair(1))

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            callback(key, menu_options[current_row])
            stdscr.refresh()
            stdscr.getch()
            break


def main():
    curses.wrapper(draw_menu, ['A', 'B', 'C'], lambda x: print(x))


if __name__ == "__main__":
    # main()
    pass
