def get_subclasses(cls):
    """
    递归地获取所有子类
    """
    return (
            cls.__subclasses__() + [g for s in cls.__subclasses__() for g in get_subclasses(s)]
    )
