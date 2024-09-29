from ..Class.NetworkPackages import NetPackage


class Join(NetPackage):
    def get(self):
        return self.name

    def __init__(self, name):
        self.name = name


class Login(NetPackage):
    def get(self):
        return self.passwd

    def __init__(self, passwd):
        self.passwd = passwd


class Logout(NetPackage):
    def get(self):
        return


class Yes(NetPackage):
    def get(self):
        return True


class No(NetPackage):
    def get(self):
        return False
