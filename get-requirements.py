import ast
import os
import re
from stdlib_list import stdlib_list


def is_camel_case(s: str):
    return re.match(
        r'^[A-Z][a-zA-Z0-9]*([A-Z][a-zA-Z0-9]*)*$',
        s
    )


def read(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        return f.read()


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]


def check_import(tree):
    res = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                print("Name:", n.name)
                res.add(n.name.split('.')[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            print("Module:", node.module)
            res.add(node.module.split('.')[0])
    return res


modules = set()

for dirpath, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if get_file_ext(filename) == '.py':
            tree = ast.parse(read(os.path.join(dirpath, filename)))
            modules |= check_import(tree)
            for m in modules.copy():
                if m + '.py' in dirnames or m + '.py' in filenames:
                    modules -= {m}
                if is_camel_case(m):
                    modules -= {m}

modules -= {'src', 'tests'}
modules -= set(stdlib_list('3.12'))

for m in modules.copy():
    if m.startswith('_'):
        modules.remove(m)
    if m.startswith('win32'):
        modules.remove(m)
        modules |= {'pywin32'}

print(list(modules))

