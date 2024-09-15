import ast
import builtins
from types import ModuleType


def _literal_eval(node, globals_: dict | None, locals_: dict | None, builtins: dict | None):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.FormattedValue):  # <formatted value>
        return _literal_eval(node.value, globals_, locals_, builtins)
    elif isinstance(node, ast.List):  # [ast.literal_eval(item) for item in node.elts]
        return [_literal_eval(element, globals_, locals_, builtins) for element in node.elts]
    elif isinstance(node, ast.Tuple):  # tuple(ast.literal_eval(item) for item in node.elts)
        return tuple(_literal_eval(element, globals_, locals_, builtins) for element in node.elts)
    elif isinstance(node,
                    ast.Dict):  # {ast.literal_eval(k): ast.literal_eval(v) for k, v in zip(node.keys, node.values)}
        return {
            _literal_eval(key, globals_, locals_, builtins):
                _literal_eval(value, globals_, locals_, builtins) for key, value in
            zip(node.keys, node.values)
        }
    elif isinstance(node, ast.Name):  # <variable>
        return locals_.get(node.id, globals_.get(node.id, builtins.get(node.id)))
    else:
        raise ValueError("Unsupported type: " + str(type(node)))


def literal_eval(string, globals_: dict | None = None, locals_: dict | None = None, builtins: dict | ModuleType | None = None):
    if isinstance(builtins, ModuleType) and builtins.__name__ == "builtins":
        builtins = vars(builtins)
    if globals_ is None:
        globals_ = {}
    if locals_ is None:
        locals_ = {}
    if builtins is None:
        builtins = {}
    tree = ast.parse(string, mode='eval')
    return _literal_eval(tree.body, globals_, locals_, builtins)


if __name__ == '__main__':
    text = """
    [1, 2, 3, __name__, print("你好")]
    """.lstrip().rstrip()
    print(literal_eval(text, globals(), locals(), builtins))
