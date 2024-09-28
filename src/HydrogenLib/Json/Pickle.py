import jsonpickle


def encode(data, indent=None):
    """
    return jsonpickle.encode(data, indent=indent)
    """
    return jsonpickle.encode(data, indent=indent)


def decode(data):
    """
    return jsonpickle.decode(data)
    """
    return jsonpickle.decode(data)


def dump(data, file, *args, **kwargs):
    """
    编码对象并储存到文件
    """
    with open(file, 'w') as f:
        f.write(
            jsonpickle.encode(data, *args, **kwargs)
        )


def load(file, *args, **kwargs):
    """
    从文件解码对象
    """
    return jsonpickle.decode(
        open(file).read(),
        *args, **kwargs
    )
