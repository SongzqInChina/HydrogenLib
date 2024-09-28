import json.decoder

from .Json import Json, Pickle


def read(file, mode='r'):
    """
    从文件读取数据，允许自定义模式
    """
    with open(file, mode) as f:
        return f.read()


def write(data, file, mode='w'):
    """
    向文件写入数据，允许自定义模式
    """
    with open(file, mode) as f:
        f.write(data)


def empty(file):
    """
    判断文件内容是否为空
    """
    with open(file) as f:
        d = f.read(1)
        if d == '':
            return True


def isspace(file):
    """
    判断文件内容是否为空白
    """
    d = read(file)
    return d.isspace()


class JsonDict(dict):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.update(Json.load(file))

    def save(self):
        Json.dump(self, self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


class JsonList(list):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.extend(Json.load(file))

    def save(self):
        Json.dump(self, self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


class JsonBaseType:
    def __init__(self, file):
        self.file = file
        self.data = Json.load(file)
        if not isinstance(
                self.data, int | float | str
        ):
            raise TypeError(
                f"{self.__class__.__name__} can only be used with base types"
            )

    def save(self):
        Json.dump(self.data, self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


class JsonPickleDict(dict):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.update(Pickle.load(file))

    def save(self):
        Pickle.dump(self, self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


class JsonPickleList(list):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.extend(Pickle.load(file))

    def save(self):
        Pickle.dump(self, self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


class JsonPickleBaseType:
    def __init__(self, file):
        self.file = file
        try:
            self.data = Pickle.load(file)
        except json.decoder.JSONDecodeError:
            self.data = None
        if not isinstance(
                self.data, int | float | str
        ):
            raise TypeError(
                f"{self.__class__.__name__} can only be used with base types"
            )

    def save(self):
        Pickle.dump(self.data, self.file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()


def json_open(file):
    dtype = type(Json.load(file))
    if empty(file) or isspace(file):
        return None
    if dtype == dict:
        return JsonDict(file)
    elif dtype == list:
        return JsonList(file)
    elif dtype == int or dtype == float or dtype == str:
        return JsonBaseType(file)
    else:
        raise TypeError(f"Unknown type: {dtype}")


def pickle_open(file):
    if empty(file) or isspace(file):
        return None
    dtype = type(Pickle.load(file))
    if dtype == dict:
        return JsonPickleDict(file)
    elif dtype == list:
        return JsonPickleList(file)
    else:
        return JsonPickleBaseType(file)


def json_safe_open(file, dtype=dict):
    if empty(file) or isspace(file):
        Json.dump(dtype(), file)
    return json_open(file)


def pickle_safe_open(file, dtype):
    if empty(file) or isspace(file):
        Pickle.dump(dtype(), file)

    return pickle_open(file)


def json_read(file):
    return Json.load(file)


def json_write(data, file):
    return Json.dump(data, file)


def pickle_read(file):
    return Pickle.load(file)


def pickle_write(data, file):
    return Pickle.dump(data, file)


