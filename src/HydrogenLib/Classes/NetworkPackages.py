from abc import abstractmethod, ABC
from jsonpickle import jsonpickler

class NetPackage(ABC):
    @abstractmethod
    def get(self): ...

    @classmethod
    def is_package(cls, package_object):
        return isinstance(package_object, cls) or issubclass(package_object.__class__, cls)

    @jsonpickler
    @abstractmethod
    def __jsonpickled__(self, context):
        pass

    @classmethod
    @jsonpickler
    @abstractmethod
    def __jsonunpickled__(cls, data, context):
        pass

class Request(NetPackage):
    def __init__(self, header=None, data=None):
        self.header = {} if header is None else header
        self.data = data

    def get(self):
        return self.header, self.data

    @jsonpickler
    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "data": self.data
        }

    @classmethod
    @jsonpickler
    def __jsonunpickled__(cls, data, context):
        return cls(
            header=data["header"],
            data=data['data']
        )

class Answer(NetPackage):
    def __init__(self, header=None, result=None, status=None):
        self.header = header
        self.result = result
        self.status = status

    def get(self):
        return self.header, self.result, self.status

    @jsonpickler
    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "result": self.result,
            "status": self.status
        }

    @classmethod
    @jsonpickler
    def __jsonunpickled__(cls, data, context):
        return cls(
            header=data['header'],
            result=data['result'],
            status=data['status']
        )

class Error(NetPackage):
    @classmethod
    @jsonpickler
    def __jsonunpickled__(cls, data, context):
        return cls(data['header'], data['error'], data['reason'])

    def __init__(self, header=None, error=None, reason=None):
        self.header = header
        self.error = error
        self.reason = reason

    def get(self):
        return self.header, self.error, self.reason

    @jsonpickler
    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "error": self.error,
            "reason": self.reason
        }

class Info(NetPackage):
    def __init__(self, header=None, info=None):
        self.header = header
        self.info = info

    def get(self):
        return self.header, self.info

    @jsonpickler
    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "info": self.info
        }

    @classmethod
    @jsonpickler
    def __jsonunpickled__(cls, data, context):
        return cls(header=data['header'], info=data['info'])

class Action(NetPackage):
    def __init__(self, header=None, action=None):
        self.header = header
        self.action = action

    def get(self):
        return self.header, self.action

    @jsonpickler
    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "action": self.action
        }

    @classmethod
    @jsonpickler
    def __jsonunpickled__(cls, data, context):
        return cls(header=data['header'], action=data['action'])
