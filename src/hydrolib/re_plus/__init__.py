import re


class BaseRe:
    pattern = None

    def match(self, string):
        return re.match(self.pattern, string)

    def findall(self, string):
        return re.findall(self.pattern, string)

    def finditer(self, string):
        return re.finditer(self.pattern, string)

    def __str__(self):
        return self.pattern


class Re(BaseRe):
    def __init__(self, pattern):
        self.pattern = pattern


class Literal(BaseRe):
    def __init__(self, literal):
        self.pattern = re.escape(literal)
