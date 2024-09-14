from ..Classes.Auto import AutoJsonPickler
from ..Time import Timer


class Result(AutoJsonPickler):
    _pickle_attrs = (
        "ext_res", "real_res",
        "elapsed_time", "start_time",
        "error"
    )

    def __init__(self):
        self.ext_res = None
        self.real_res = None
        self.elapsed_time = None
        self.start_time = None
        self.error = None

    def success(self):
        return self.error is None and self.real_res == self.ext_res


class Results(AutoJsonPickler):
    _pickle_attrs = (
        "errors", "successes", "fails"
    )

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


class Point(AutoJsonPickler):
    _pickle_attrs = (
        "except_res", "args", "kwargs"
    )

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

    def run(self, func):
        res = Result()
        res.ext_res = self.except_res
        timer = Timer()
        try:
            timer.start()
            rt = func(*self.args, **self.kwargs)
            timer.end()
            res.real_res = rt
            res.start_time = timer.start_time
            res.elapsed_time = timer.res
        except Exception as e:
            res.error = e
        return res


class Points(AutoJsonPickler):
    _pickle_attrs = (
        "points"
    )

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
