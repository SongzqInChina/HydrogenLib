from ..Class.NetworkPackages import NetPackage


class RequestToJoin(NetPackage):
    def get(self):
        return self.name

    def __init__(self, name):
        self.name = name


class Login(NetPackage):
    def get(self):
        return self.passwd

    def __init__(self, passwd):
        self.passwd = passwd
