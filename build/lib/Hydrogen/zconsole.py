import os

import psutil
import win32con
import win32console
import win32gui
import win32security


def command_shell():
    ps = psutil.Process(os.getppid())
    if ps.name() in ['py.exe', 'pyw.exe']:
        return 'Python'
    if ps.name() == 'powershell.exe':
        return "Powershell"
    if ps.name() == 'cmd.exe':
        return "Cmd"
    return ps.name()

