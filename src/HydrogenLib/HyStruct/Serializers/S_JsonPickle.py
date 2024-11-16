import jsonpickle

from . import S_Json as JsonBase


class JsonPickle(JsonBase.Json):
    def dumps(self, data):
        jsonpickle.dumps(data)

    def loads(self, data):
        return jsonpickle.loads(data)
