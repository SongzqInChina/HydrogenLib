def singleton_decorator(cls):
    class wrap(cls):
        _Instance = None

        def __new__(cls, *args, **kwargs):
            if wrap._Instance is None:
                wrap._Instance = super().__new__(cls, *args, **kwargs)
            return wrap._Instance

        def __str__(self):
            return super().__str__()

        def __repr__(self):
            return super().__repr__()

    return wrap


def Instance(*args, **kwargs):
    def wrapper(cls):
        return cls(*args, **kwargs)

    return wrapper
