def singleton_decorator(classic):
    class wrap(classic):
        _Instance = None

        def __new__(cls, *args, **kwargs):
            if wrap._Instance is None:
                wrap._Instance = super().__new__(cls, *args, **kwargs)
            return wrap._Instance

    return wrap
