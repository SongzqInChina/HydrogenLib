import os


def split_env_value(*env_value):
    for i in env_value:
        yield i.split(';')


def get_env_dict():
    env_dict = os.environ.copy()
    return {
        k: split_env_value(v) for k, v in env_dict.items()
    }
