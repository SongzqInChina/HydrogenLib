import argparse as module
import os

import psutil


def command_shell():
    ps = psutil.Process(os.getppid())
    if ps.name() in ['py.exe', 'pyw.exe']:
        return 'Python'
    if ps.name() == 'powershell.exe':
        return "Powershell"
    if ps.name() == 'cmd.exe':
        return "Cmd"
    return ps.name()


ArgParser = module.ArgumentParser
