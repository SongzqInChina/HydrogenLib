import json
import logging
from typing import Any

import jsonpickle

"""
所有类都用于解析JSON表达式
"""

zjson_logger = logging.getLogger("SzQlib.zjson")


# module end

class json_simple:
    @staticmethod
    def encode(data):
        return json.dumps(data, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def decode(data):
        return json.loads(data)


class pickle_simple:
    @staticmethod
    def encode(data) -> str:
        return jsonpickle.encode(data)

    @staticmethod
    def decode(data) -> Any:
        return jsonpickle.decode(data)


class json_free:
    @staticmethod
    def encode(data, indent=4):
        return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=indent)

    @staticmethod
    def decode(data):
        return json.loads(data)


class pickle_free:
    @staticmethod
    def encode(data, indent=4):
        return jsonpickle.encode(data, indent=indent)

    @staticmethod
    def decode(data):
        return jsonpickle.decode(data)


zjson_logger.debug("Module zjson loading ...")
