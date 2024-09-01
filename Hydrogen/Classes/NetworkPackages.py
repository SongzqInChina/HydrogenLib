from abc import abstractmethod, ABC


class NetPackage(ABC):
    @abstractmethod
    def get(self): ...

    @abstractmethod
    def __jsonpickled__(self, context): ...

    @classmethod
    @abstractmethod
    def __jsonpickler__(cls, data, context): ...

    @classmethod
    def is_package(cls, package_object):
        return isinstance(package_object, cls) or issubclass(package_object.__class__, cls)


class Request(NetPackage):
    def __init__(self, header=None, data=None):
        self.header = {} if header is None else header
        self.data = data

    def get(self):
        return self.header, self.data

    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "data": self.data
        }

    @classmethod
    def __jsonpickler__(cls, data, context):
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

    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "result": self.result,
            "status": self.status
        }

    @classmethod
    def __jsonpickler__(cls, data, context):
        return cls(
            header=data['header'],
            result=data['result'],
            status=data['status']
        )


class Error(NetPackage):
    @classmethod
    def __jsonpickler__(cls, data, context):
        return cls(data['header'], data['error'], data['reason'])

    def __init__(self, header=None, error=None, reason=None):
        self.header = header
        self.error = error
        self.reason = reason

    def get(self):
        return self.header, self.error, self.reason

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

    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "info": self.info
        }

    @classmethod
    def __jsonpickler__(cls, data, context):
        return cls(header=data['header'], info=data['info'])


class Action(NetPackage):
    def __init__(self, header=None, action=None):
        self.header = header
        self.action = action

    def get(self):
        return self.header, self.action

    def __jsonpickled__(self, context):
        return {
            "header": self.header,
            "action": self.action
        }

    @classmethod
    def __jsonpickler__(cls, data, context):
        return cls(header=data['header'], action=data['action'])