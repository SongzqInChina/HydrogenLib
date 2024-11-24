import src.hydrolib.codedoc.Struct
from src.hydrolib.codedoc.Struct import CodeStruct


def get():
    print(src.HydrogenLib.Doc.Struct.get_called_func(depth=1))


def get_wrap():
    return get()


def call():
    get_wrap()


# <module> call, get_wrap, get, get_called_func
# 4         3       2       1           0
call()

def doctest():
    main = src.HydrogenLib.Doc.Struct.CodeStructMain('main', 'main')
    with CodeStruct('main', ''):
        with CodeStruct('sub', ''):
            ...
        with CodeStruct('sub2', ''):
            ...
    with CodeStruct('main2', ''):
        ...
    print(
        main.generate_tree_str()
    )

doctest()
