import os
import sys
import types
import winreg


def add_to_startup(name, file_path=""):
    # By IvanHanloth
    if file_path == "":
        file_path = os.path.realpath(sys.argv[0])
    auth = "IvanHanloth"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run",
                         winreg.KEY_SET_VALUE,
                         winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, file_path)
    winreg.CloseKey(key)


def remove_from_startup(name):
    auth = "IvanHanloth"

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run",
                         winreg.KEY_SET_VALUE,
                         winreg.KEY_ALL_ACCESS | winreg.KEY_WRITE | winreg.KEY_CREATE_SUB_KEY)  # By IvanHanloth
    try:
        winreg.DeleteValue(key, name)

    except FileNotFoundError:
        print(f"{name} not found in startup.")
    else:
        print(f"{name} removed from startup.")

    winreg.CloseKey(key)


def value_HKEY(name):
    reg_path_l = name
    reg = winreg.HKEY_LOCAL_MACHINE
    if reg_path_l == "HKEY_CURRENT_USER":   reg = winreg.HKEY_CURRENT_USER
    if reg_path_l == "HKEY_LOCAL_MACHINE":  reg = winreg.HKEY_LOCAL_MACHINE
    if reg_path_l == "HEKY_CLASSES_ROOT":   reg = winreg.HKEY_CLASSES_ROOT
    if reg_path_l == "HEKY_USERS":          reg = winreg.HKEY_USERS
    if reg_path_l == "HEKY_CURRENT_CONFIG": reg = winreg.HKEY_CURRENT_CONFIG

    return reg


def value_HKEY_PATH(reg_path):
    reg = winreg.HKEY_LOCAL_MACHINE

    reg_path_l = reg_path.split('\\')[0]

    reg_path = '\\'.join(reg_path.split('\\')[1::])

    if reg_path_l == "HKEY_CURRENT_USER":   reg = winreg.HKEY_CURRENT_USER
    if reg_path_l == "HKEY_LOCAL_MACHINE":  reg = winreg.HKEY_LOCAL_MACHINE
    if reg_path_l == "HEKY_CLASSES_ROOT":   reg = winreg.HKEY_CLASSES_ROOT
    if reg_path_l == "HEKY_USERS":          reg = winreg.HKEY_USERS
    if reg_path_l == "HEKY_CURRENT_CONFIG": reg = winreg.HKEY_CURRENT_CONFIG

    return reg


def all_KeyValue(reg_path: str):
    """
    sepstr be \\
    """
    d = {}

    reg = winreg.HKEY_CURRENT_USER
    reg_path_l = reg_path.split('\\')[0]
    reg_path = '\\'.join(reg_path.split('\\')[1::])

    if reg_path_l == "HKEY_CURRENT_USER":   reg = winreg.HKEY_CURRENT_USER
    if reg_path_l == "HKEY_LOCAL_MACHINE":  reg = winreg.HKEY_LOCAL_MACHINE
    if reg_path_l == "HEKY_CLASSES_ROOT":   reg = winreg.HKEY_CLASSES_ROOT
    if reg_path_l == "HEKY_USERS":          reg = winreg.HKEY_USERS
    if reg_path_l == "HEKY_CURRENT_CONFIG": reg = winreg.HKEY_CURRENT_CONFIG

    try:
        key = winreg.OpenKey(reg, reg_path)
    except Exception as ex:
        return d

    # 获取该键的所有键值，遍历枚举
    try:
        i = 0
        while 1:
            # EnumValue方法用来枚举键值，EnumKey用来枚举子键
            name, value, type = winreg.EnumValue(key, i)
            d[name] = (name, value, type)
            i += 1
    except Exception:
        pass

    return d


def add_reg_key(reg_path):
    r"""
    sepstr only be '\\'
    """
    reg = winreg.HKEY_CURRENT_USER
    reg_path_l = reg_path.split('\\')[0]

    reg_path = '\\'.join(reg_path.split('\\')[1::])

    if reg_path_l == "HKEY_CURRENT_USER":   reg = winreg.HKEY_CURRENT_USER
    if reg_path_l == "HKEY_LOCAL_MACHINE":  reg = winreg.HKEY_LOCAL_MACHINE
    if reg_path_l == "HEKY_CLASSES_ROOT":   reg = winreg.HKEY_CLASSES_ROOT
    if reg_path_l == "HEKY_USERS":          reg = winreg.HKEY_USERS
    if reg_path_l == "HEKY_CURRENT_CONFIG": reg = winreg.HKEY_CURRENT_CONFIG

    try:
        key = winreg.OpenKey(reg, reg_path)
    except:
        key = winreg.CreateKey(reg, reg_path)

    winreg.CloseKey(key)


classInfo = type | types.UnionType | tuple[object, ...]


def pyTypeToRegTypeA(pyType: object, big_type: bool = False):
    if isinstance(pyType, int):  # pyType为int
        if big_type:
            return winreg.REG_QWORD
        else:
            return winreg.REG_DWORD
    elif isinstance(pyType, float):  # pyType = float
        return ValueError("REG types not have 'float'.")
    elif isinstance(pyType, str):
        if big_type:
            return winreg.REG_EXPAND_SZ
        else:
            return winreg.REG_SZ
    else:
        return ValueError(f"pyType '{pyType}' don't turn to 'REG_TYPE'.")


def spilt_regPath(reg_path: str):
    reg = value_HKEY_PATH(reg_path)
    path = '\\'.join(reg_path.split('\\')[1::])
    return reg, path


def setRegKey(reg_path: str, type: int):
    r"""
    reg_path
        path.name=value
    HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer.DisallowRun=1
    """
    after = reg_path.split('.')
    value = after[1].split('=')[1::]
    value = ''.join(value)
    name = after[1].split('=')[0]
    r, p = spilt_regPath(reg_path)
    p = spilt_regPath(after[0])[1]
    k = winreg.OpenKey(r, p, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(k, name, 0, type, value)
