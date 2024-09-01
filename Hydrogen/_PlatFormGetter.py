import platform

Windows = 'Windows'
MacOS = 'Darwin'
Linux = 'Linux'


def is_win():
    return platform.system() == Windows


def is_mac():
    return platform.system() == MacOS


def is_linux():
    return platform.system() == Linux
