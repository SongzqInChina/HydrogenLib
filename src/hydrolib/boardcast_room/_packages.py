from ..utils.NetworkPackages import NetPackage


class Register(NetPackage):
    _str_attrs = ("name",)
    __state_attrs__ = ("name",)

    def get(self):
        return self.name

    def __init__(self, name):
        self.name = name


class Unregister(NetPackage):
    def get(self):
        return


class Broadcast(NetPackage):
    _str_attrs = ("data",)
    __state_attrs__ = ("data",)
    """
    请求广播的客户端使用
    """

    def __init__(self, data):
        self.data = data

    def get(self):
        return self.data


class Data(NetPackage):
    _str_attrs = ("data",)
    __state_attrs__ = ("data",)
    """
    向所有客户端广播信息的服务端使用
    """

    def __init__(self, data):
        self.data = data

    def get(self):
        return self.data


class OK(NetPackage):
    def get(self):
        return True


class Deny(NetPackage):
    _str_attrs = ("reason",)
    __state_attrs__ = ("reason",)
    def __init__(self, reason):
        self.reason = reason

    def get(self):
        return self.reason
