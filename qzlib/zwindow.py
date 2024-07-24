import json
import tkinter as tk

import win32api
import win32con
import win32gui
import win32process

from .zprocessx import CProcess

MB_OK = 0
MB_OK_CLEAN = 1
MB_STOP_AGAIN_CLEAN = 2
MB_YES_NO_CLEAN = 3
MB_YES_NO = 4
MB_AGAIN_CLEAN = 5

EB_OK = 16
EB_OK_CLEAN = 17
EB_STOP_AGAIN_CLEAN = 18
EB_YES_NO_CLEAN = 19
EB_YES_NO = 20
EB_AGAIN_CLEAN = 21

AB_OK = 32
AB_OK_CLEAN = 33
AB_STOP_AGAIN_CLEAN = 34
AB_YES_NO_CLEAN = 35
AB_YES_NO = 36
AB_AGAIN_CLEAN = 37

WB_OK = 48
WB_OK_CLEAN = 49
WB_STOP_AGAIN_CLEAN = 50
WB_YES_NO_CLEAN = 51
WB_YES_NO = 52
WB_AGAIN_CLEAN = 53

TB_OK = 64
TB_OK_CLEAN = 65
TB_STOP_AGAIN_CLEAN = 66
TB_YES_NO_CLEAN = 67
TB_YES_NO = 68
TB_AGAIN_CLEAN = 69

OK = MB_OK
OK_CLEAN = MB_OK_CLEAN
YES_NO = MB_YES_NO
STOP_AGAIN_CLEAN = MB_STOP_AGAIN_CLEAN
YES_NO_CLEAN = MB_YES_NO_CLEAN

BUTTON_YES = 1
BUTTON_CANNEL = 2
BUTTON_STOP = 3
BUTTON_AGAIN = 4
BUTTON_NEXT = 5
BUTTON_TRUE = 6
BUTTON_FALSE = 7
BUTTON_TRY_AGAIN = 10


class Box:
    _AB = {
        0: AB_OK,
        1: AB_OK_CLEAN,
        2: AB_STOP_AGAIN_CLEAN,
        3: AB_YES_NO_CLEAN,
        4: AB_YES_NO,
        5: AB_AGAIN_CLEAN
    }
    _TB = {
        0: TB_OK,
        1: TB_OK_CLEAN,
        2: TB_STOP_AGAIN_CLEAN,
        3: TB_YES_NO_CLEAN,
        4: TB_YES_NO,
        5: TB_AGAIN_CLEAN
    }
    _WB = {
        0: WB_OK,
        1: WB_OK_CLEAN,
        2: WB_STOP_AGAIN_CLEAN,
        3: WB_YES_NO_CLEAN,
        4: WB_YES_NO,
        5: WB_AGAIN_CLEAN
    }
    _EB = {
        0: EB_OK,
        1: EB_OK_CLEAN,
        2: EB_STOP_AGAIN_CLEAN,
        3: EB_YES_NO_CLEAN,
        4: EB_YES_NO,
        5: EB_AGAIN_CLEAN
    }
    _MB = {
        0: MB_OK,
        1: MB_OK_CLEAN,
        2: MB_STOP_AGAIN_CLEAN,
        3: MB_YES_NO_CLEAN,
        4: MB_YES_NO,
        5: MB_AGAIN_CLEAN
    }

    @property
    def get(self) -> dict: return dict()

    def __getitem__(self, item: int) -> int:
        return self.get[item]


class MB(Box):
    @property
    def get(self):
        return self._MB


class EB(Box):
    @property
    def get(self):
        return self._EB


class AB(Box):
    @property
    def get(self):
        return self._AB


class TB(Box):
    @property
    def get(self):
        return self._TB


class WB(Box):
    @property
    def get(self):
        return self._WB


def msgbox(message, title, uType, *, msg_class: type[Box] | None = MB):
    """
    nType对应的对话框
    - 0: 确定
    - 1: 确定，取消
    - 2: 终止，重试，忽略
    - 3: 是，否，取消
    - 4: 是，否
    - 5: 重试，取消
    - 6: 取消，再试一次，继续(注:Windows NT下不支持)\n
    返回值对应的值
    - 1: 确定
    - 2: 取消
    - 3: 终止
    - 4: 重试
    - 5: 忽略
    - 6: 是
    - 7: 否
    - 10:重试
    - 11:继续

    """
    if msg_class == None:
        msg_class = MB

    return win32api.MessageBox(0, message, title, msg_class().get[uType], 0)


def inputbox(msg="", title="", default=''):
    result = tk.simpledialog.askstring(title, msg, initialvalue=default)
    return result


def handles():
    def callback(__hwnd, __hwnds):
        __hwnds += (__hwnd, )

    hwnds = ()
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


class _WinStat:
    def __init__(self, stat, father_class):
        self.stat = stat
        self.flag = stat[0]
        self.last_command = stat[1]
        self.min_mized_pos = stat[2]
        self.max_mized_pos = stat[3]
        self.normal_rect = stat[4]
        self.rect_x = self.normal_rect[0]
        self.rect_y = self.normal_rect[1]
        self.rect_width = self.normal_rect[2]
        self.rect_height = self.normal_rect[3]
        self.father = father_class  # type: Win32Window

    def is_maximized(self):
        return self.flag == win32con.WS_MAXIMIZE

    def is_minimized(self):
        return self.flag == win32con.WS_MINIMIZE

    def is_normal(self):
        return self.flag not in (win32con.WS_MAXIMIZE, win32con.WS_MINIMIZE)

    def is_visible(self):
        return self.flag == win32con.WS_VISIBLE

    def is_enabled(self):
        return self.father.enable() and self.father.visible() and self.is_visible()

    def to_dict(self):
        d = dict(
            is_maximized=self.is_maximized(),
            is_visible=self.is_visible(),
            is_enabled=self.is_enabled(),
            is_minimized=self.is_minimized(),
            is_normal=self.is_normal(),
            flag=self.flag,
            last_command=self.last_command,
            min_mized_pos=self.min_mized_pos,
            max_mized_pos=self.max_mized_pos,
            stat=self.stat,
            rect=self.normal_rect,
            x=self.rect_x,
            y=self.rect_y,
            width=self.rect_width,
            height=self.rect_height
        )
        return d

    def __str__(self):
        return rf"WinStat({self.to_dict()})"


class Win32Window:
    _hwnd = None

    def __init__(self, hwnd=None):
        self._hwnd = hwnd
        self._old_style = None

    @property
    def hwnd(self):
        return self._hwnd

    @hwnd.setter
    def hwnd(self, hwnd):
        if hwnd in handles():
            self._hwnd = hwnd
        else:
            raise "无效的窗口句柄"

    def destroy(self):
        return win32gui.DestroyWindow(self._hwnd)

    def send(self, msg, wparam=0, lparam=0):
        return win32gui.SendMessage(self._hwnd, msg, wparam, lparam)

    def post(self, msg, wparam=0, lparam=0):
        return win32gui.PostMessage(self._hwnd, msg, wparam, lparam)

    def move(self, x, y, width, height, bRepaint=True):
        return win32gui.MoveWindow(self._hwnd, x, y, width, height, bRepaint)

    def title(self, new_title=None):
        if new_title is None:
            return win32gui.GetWindowText(self._hwnd)
        else:
            return win32gui.SetWindowText(self._hwnd, new_title)

    def visible(self, vis: bool | None = None):
        if vis is None:
            return win32gui.IsWindowVisible(self._hwnd)
        else:
            return win32gui.ShowWindow(self._hwnd, win32con.SW_SHOW if vis else win32con.SW_HIDE)

    def remove_border(self):
        current_style = self.getlong(win32con.GWL_STYLE)
        new_style = current_style & ~(win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_THICKFRAME)
        self.setlong(win32con.GWL_STYLE, new_style)
        self.update()

    def add_border(self):
        current_style = self.getlong(win32con.GWL_STYLE)
        new_style = current_style | (win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_THICKFRAME)
        self.setlong(win32con.GWL_STYLE, new_style)
        self.update()

    def enable(self, state: bool | None = None):
        if state is None:
            return win32gui.IsWindowEnabled(self._hwnd)
        elif isinstance(state, bool):
            return win32gui.EnableWindow(self._hwnd, state)
        else:
            raise ValueError("state should be a boolean or None")

    def show(self, nCmdShow):
        return win32gui.ShowWindow(self._hwnd, nCmdShow)

    def set_position(self, x=None, y=None, width=None, height=None, after=None, flags=0):
        """
        设置窗口位置和尺寸。如果不提供参数，则保持当前位置和尺寸不变。

        :param x: 新的左上角x坐标，默认为当前坐标。
        :param y: 新的左上角y坐标，默认为当前坐标。
        :param width: 新的窗口宽度，默认为当前宽度。
        :param height: 新的窗口高度，默认为当前高度。
        :param after: 窗口排列顺序标志，默认插入到Z序顶部（SWP_NOMOVE保持位置不变）。
        :param flags: 额外的设置窗口位置标志，默认为0。
        """
        hWndInsertAfter = after if after is not None else win32con.HWND_TOP  # 默认置于所有窗口之上
        current_rect = win32gui.GetWindowRect(self._hwnd)

        # 使用当前尺寸和位置作为默认值，如果用户没有指定
        newX = x if x is not None else current_rect[0]
        newY = y if y is not None else current_rect[1]
        newWidth = width if width is not None else (current_rect[2] - current_rect[0])
        newHeight = height if height is not None else (current_rect[3] - current_rect[1])

        # 如果用户只想改变Z序而不移动窗口，需要特别处理
        if after is None:
            flags |= win32con.SWP_NOMOVE

        # 调用SetWindowPos设置新位置和尺寸
        return win32gui.SetWindowPos(self._hwnd, hWndInsertAfter, newX, newY, newWidth, newHeight, flags)

    def rect(self):
        return win32gui.GetWindowRect(self._hwnd)

    def update(self):
        return win32gui.UpdateWindow(self._hwnd)

    def top(self):
        return win32gui.BringWindowToTop(self._hwnd)

    def active(self):
        return win32gui.SetActiveWindow(self._hwnd)

    def child(self):
        return self.__class__(win32gui.GetWindow(self._hwnd, win32con.GW_CHILD))

    def close(self):
        return win32gui.DestroyWindow(self._hwnd)

    def parent(self):
        return self.__class__(win32gui.GetParent(self._hwnd))

    def foreground(self):
        return win32gui.SetForegroundWindow(self._hwnd)

    def getlong(self, index, flags=0):
        return win32gui.GetWindowLong(self._hwnd, index, flags)

    def setlong(self, index, value, flags=0):
        return win32gui.SetWindowLong(self._hwnd, index, value, flags)

    def flash(self, count=0):
        win32gui.FlashWindow(self._hwnd, count)

    def controls(self):
        controls = []

        def wrap(hwnd, param):
            info = {
                "hwnd": hwnd,
                "class": win32gui.GetClassName(hwnd),
                "text": win32gui.GetWindowText(hwnd)
            }
            controls.append(info)
            return True

        win32gui.EnumChildWindows(self._hwnd, wrap, None)

        return controls

    @classmethod
    def htow(cls, hwnd):
        return cls(hwnd)

    def wtoh(self):
        return self.hwnd

    def _process(self):
        return win32process.GetWindowThreadProcessId(self._hwnd)

    def process(self) -> int:
        return self._process()[1]

    def thread(self) -> int:
        return self._process()[0]

    def stat(self):
        stat = win32gui.GetWindowPlacement(self._hwnd)
        return _WinStat(stat, self)

    def __getattribute__(self, item):
        hwnd = object.__getattribute__(self, "_hwnd")
        if hwnd not in handles():
            raise OSError(f"HWND {hwnd} is not valid")
        else:
            return object.__getattribute__(self, item)

    def __str__(self):
        return str(dict(
            {
                "hwnd": self._hwnd,
                "title": self.title(),
                "process": self.process(),
                "thread": self.thread(),
                "rect": self.rect(),
                "visible": self.visible(),
                "enabled": self.enable(),
                "foreground": self.foreground(),
                "active": self.active(),
                "top": self.top(),
                "parent": self.parent(),
                "img_name": CProcess(self.process())
            }
        ))


def windows():
    return (Win32Window(hwnd) for hwnd in handles())


def find(title=None, classname=None):
    return win32gui.FindWindow(classname, title)


def wtoh(window: Win32Window):
    return window.hwnd


def htow(hwnd):
    if hwnd in handles():
        return Win32Window(hwnd)
    return None
