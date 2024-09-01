import json
import logging

import jsonpickle

from .Const import JSON_DECODE, JSON_ENCODE

"""
所有类都用于解析JSON表达式
"""

Json_logger = logging.getLogger("SzQlib.Json")


# module end


class Json:
    @staticmethod
    def encode(data, indent=4):
        return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=indent)

    @staticmethod
    def decode(data):
        return json.loads(data)

    @classmethod
    def __call__(cls, opt, obj, *args, **kwargs):
        if opt == JSON_DECODE:
            return cls.decode(obj)
        elif opt == JSON_ENCODE:
            return cls.encode(obj, *args, **kwargs)
        else:
            raise ValueError("Invalid opt")


class Pickle:
    @staticmethod
    def encode(data, indent=4):
        return jsonpickle.encode(data, indent=indent)

    @staticmethod
    def decode(data):
        return jsonpickle.decode(data)

    @classmethod
    def __call__(cls, opt, obj, *args, **kwargs):
        if opt == JSON_DECODE:
            return cls.decode(obj)
        elif opt == JSON_ENCODE:
            return cls.encode(obj, *args, **kwargs)
        else:
            raise ValueError("Invalid opt")


Json_logger.debug("Module Json loading ...")
