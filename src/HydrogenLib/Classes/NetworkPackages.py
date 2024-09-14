from abc import abstractmethod, ABC


class NetPackage(ABC):
    @abstractmethod
    def get(self): ...

    @classmethod
    def is_package(cls, package_object):
        return isinstance(package_object, cls) or issubclass(package_object.__class__, cls)

    def __getstate__(self):
        raise NotImplementedError("This class is not picklable")

    def __setstate__(self, state):
        raise NotImplementedError("This class is not picklable")


class Request(NetPackage):
    def __init__(self, header=None, data=None):
        self.header = {} if header is None else header
        self.data = data

    def get(self):
        return self.header, self.data

    def __getstate__(self):
        return {
            "header": self.header,
            "data": self.data
        }

    def __setstate__(self, state):
        self.header = state.get("header", {})
        self.data = state.get("data", None)


class Answer(NetPackage):
    def __init__(self, header=None, result=None, status=None):
        self.header = header
        self.result = result
        self.status = status

    def get(self):
        return self.header, self.result, self.status

    def __getstate__(self):
        return {
            "header": self.header,
            "result": self.result,
            "status": self.status
        }

    def __setstate__(self, state):
        self.header = state.get("header", None)
        self.result = state.get("result", None)
        self.status = state.get("status", None)


class Error(NetPackage):
    def __init__(self, header=None, error=None, reason=None):
        self.header = header
        self.error = error
        self.reason = reason

    def get(self):
        return self.header, self.error, self.reason

    def __getstate__(self):
        return {
            "header": self.header,
            "error": self.error,
            "reason": self.reason
        }

    def __setstate__(self, state):
        self.header = state.get("header", None)
        self.error = state.get("error", None)
        self.reason = state.get("reason", None)


class Info(NetPackage):
    def __init__(self, header=None, info=None):
        self.header = header
        self.info = info

    def get(self):
        return self.header, self.info

    def __getstate__(self):
        return {
            "header": self.header,
            "info": self.info
        }

    def __setstate__(self, state):
        self.header = state.get("header", None)
        self.info = state.get("info", None)


class Action(NetPackage):
    def __init__(self, header=None, action=None):
        self.header = header
        self.action = action

    def get(self):
        return self.header, self.action

    def __getstate__(self):
        return {
            "header": self.header,
            "action": self.action
        }

    def __setstate__(self, state):
        self.header = state.get("header", None)
        self.action = state.get("action", None)
