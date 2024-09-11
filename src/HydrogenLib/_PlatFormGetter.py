import os


def is_win():
    return os.name == 'nt'


def is_linux():
    return os.name == 'posix'


def is_mac():
    return os.name == 'mac'
