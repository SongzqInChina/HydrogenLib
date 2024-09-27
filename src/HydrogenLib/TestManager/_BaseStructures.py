import rich.traceback

from ..Class.Auto import AutoState, AutoInfo
from ..Time import Timer


class Result(AutoState, AutoInfo):
    _state_attrs = (
        "ext_res", "real_res",
        "elapsed_time", "start_time",
        "error"
    )
    _repr_attrs = _state_attrs
    _str_attrs = _state_attrs

    def __init__(self):
        self.ext_res = None
        self.real_res = None
        self.elapsed_time = None
        self.start_time = None
        self.error = None

    def success(self):
        return self.error is None and self.real_res == self.ext_res


class Results(AutoState, AutoInfo):
    _state_attrs = (
        "errors", "successes", "fails"
    )
    _repr_attrs = _state_attrs
    _str_attrs = _state_attrs

    def __init__(self):
        self.errors: list[Result] = []
        self.successes: list[Result] = []
        self.fails: list[Result] = []

    def add_result(self, result: Result):
        if result.success():
            self.successes.append(result)
        else:
            if result.error is None:
                self.fails.append(result)
                return
            self.errors.append(result)

    def get_result(self):
        return self.successes, self.fails, self.errors

    def __iter__(self):
        return iter(self.successes + self.fails + self.errors)


class Point(AutoState, AutoInfo):
    _state_attrs = (
        "except_res", "args", "kwargs"
    )
    _repr_attrs = _state_attrs
    _str_attrs = _state_attrs

    def __init__(self):
        self.except_res = None
        self.args = ()
        self.kwargs = {}

    def set_point(self, except_res, *args, **kwargs):
        self.except_res = except_res
        self.args = args
        self.kwargs = kwargs
        return self

    def get_point(self):
        return self.except_res, self.args, self.kwargs

    def to_dict(self):
        return {
            "ext_value": self.except_res,
            "args": self.args,
            "kwargs": self.kwargs
        }

    def run(self, func):
        res = Result()
        res.ext_res = self.except_res
        timer = Timer()
        timer.start()
        try:
            rt = func(*self.args, **self.kwargs)
            timer.end()
            res.real_res = rt
        except Exception as e:
            res.error = rich.traceback.Traceback.from_exception(
                exc_type=type(e), exc_value=e, traceback=e.__traceback__
            )
        res.start_time = timer.start_time
        res.elapsed_time = timer.res
        return res


class Points(AutoState, AutoInfo):
    _state_attrs = (
        "points"
    )
    _repr_attrs = _state_attrs
    _str_attrs = _state_attrs

    def __init__(self):
        self.points = []

    def add_point(self, except_res, *args, **kwargs):
        p = Point().set_point(except_res, *args, **kwargs)
        if p in self.points:
            return False
        self.points.append(p)
        return True

    def extend_points(self, points):
        self.points.extend(points)

    def run(self, func):
        res = Results()
        for p in self.points:
            res.add_result(p.run(func))
        return res

    def __iter__(self):
        return iter(self.points)
