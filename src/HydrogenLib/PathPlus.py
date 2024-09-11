import os


def path_to(*path):
    path = os.sep.join(path)
    return path


def isdir(path):
    return os.path.isdir(path)


def isfile(file):
    return os.path.isfile(file)


def exists(path):
    return os.path.exists(path)


def mkdir(path):
    os.mkdir(path)


def mkdirs(path):
    if isdir(path):
        return
    os.makedirs(path)


def rmdir(path):
    os.rmdir(path)


def remove(path):
    os.remove(path)


def rename(old, new):
    os.rename(old, new)


def mkfile(file, clear=True):
    if not isfile(file):
        mkdirs(os.path.dirname(file))
        open(file, "w").close()
    elif clear:
        open(file, "w").close()


def listdir(path):
    return os.listdir(path)


def scandir(path):
    for i in os.scandir(path):
        try:
            name = i.name
            yield i
        except PermissionError:
            continue


def scandir_ls(path):
    return list(scandir(path))


def rmdirs(path):
    for i in scandir(path):
        if i.is_dir():
            rmdirs(i.path)
        else:
            remove(i.path)
    rmdir(path)


def rmfile(file):
    remove(file)


def abspath(path):
    return os.path.abspath(path)


def isabspath(path):
    return os.path.isabs(path)


def split(path):
    if isinstance(path, list | tuple):
        return list(path)
    else:
        path = process(path)
        pls = list(os.path.split(path))
        # 去重 \\
        return pls


def process(path) -> str:
    path = str(path)
    path = path.replace("/", "\\")
    path = path.replace("\\\\", "\\")
    return path


def _tree(folder) -> dict:
    f_dic = {folder:{}}
    now_dic = f_dic[folder]
    folder = path_to(folder)

    if isfile(folder):
        now_dic[folder] = os.path.getsize(folder)
    else:
        for i in scandir(folder):
            if i.is_dir():
                now_dic[i.path] = tree(i.path)
            else:
                now_dic[i.path] = os.path.getsize(i.path)
    return f_dic


def tree(folder):
    t = _tree(folder)
    return t


