# ast types
from src.HydrogenLib.TypeFunc.LiteralEval import literal_eval


class Expr:
    def __init__(self, expr):
        self.expr = expr

    def execute(self, globals_: dict | None = None, locals_: dict | None = None):
        return literal_eval(self.expr, globals_, locals_, builtins=True)


class Table:
    def __init__(self, attrs: dict):
        self.attrs = attrs

    def add_attr(self, name, value):
        self.attrs[name] = value

    def delete_attr(self, name):
        del self.attrs[name]

    def get_attr(self, name):
        return self.attrs[name]

    def exists(self, name):
        return name in self.attrs


class Var:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value
