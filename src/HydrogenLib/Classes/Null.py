from ..Decorators import singleton_decorator


@singleton_decorator
class _Null:
    ...


null = _Null()
