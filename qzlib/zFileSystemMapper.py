import logging

from .zpath import *

zfilesystemmapper_logger = logging.getLogger(__name__)


# module end

class File:
    def __init__(self, file):
        zfilesystemmapper_logger.debug("Create a new file attribute object")
        if not isfile(file):
            raise FileNotFoundError(file)
        self._file = file

    def _check(self):
        if not exists(self._file):
            raise FileNotFoundError(self._file)

    @property
    def size(self):
        self._check()
        return os.path.getsize(self._file)

    @property
    def data(self):
        self._check()
        with open(self._file, 'rb') as f:
            return f.read()

    @property
    def name(self):
        self._check()
        return os.path.basename(self._file)

    @property
    def fat(self):
        self._check()
        return os.path.dirname(self._file)

    def __repr__(self):
        return f'<File Object of "{self._file}">'

    __str__ = __repr__


class FileSystemMapper:  # 把文件系统（文件夹）映射成字典
    def __init__(self, path):
        zfilesystemmapper_logger.debug(f"Mapping floder({repr(path)}) to dict")
        self._path = path
        self._dic = None

    def scan(self):
        self._dic = tree(self._path)

    @property
    def scan_res(self):
        return self._dic

    def __setitem__(self, key, value):
        key = path_to(self._path, key)
        if value is None:
            if not exists(key):
                mkfile(key)
            else:
                raise FileExistsError(key)
        elif isinstance(value, str):
            with open(key, 'w') as f:
                f.write(value)
        elif value == self or isinstance(value, dict):
            if not exists(key):
                mkdir(key)
            else:
                raise FileExistsError(key)

    def __getitem__(self, key):
        if not isabspath(key):
            key = path_to(self._path, key)
        if not exists(key):
            raise FileNotFoundError(key)
        if isfile(key):
            return File(key)
        if isdir(key):
            return self.__class__(key)

    def __delitem__(self, key):
        self.pop(key)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False

    def get(self, key):
        key = path_to(self._path, key)
        try:
            return self[key]
        except FileNotFoundError:
            return None

    def pop(self, key):
        key = path_to(self._path, key)
        if exists(key):
            data = self[key].data
            if isfile(key):
                rmfile(key)
            if isdir(key):
                rmdirs(key)
            return data
        else:
            raise FileNotFoundError(key)


zfilesystemmapper_logger.debug("Module zFileSystemMapper loading ...")
