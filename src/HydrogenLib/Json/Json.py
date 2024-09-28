import json


def encode(data, indent=None):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=indent)


def decode(data):
    return json.loads(data)


def dump(data, file, *args, **kwargs):
    return json.dump(data, file, *args, **kwargs)


def load(file, *args, **kwargs):
    return json.load(file, *args, **kwargs)
