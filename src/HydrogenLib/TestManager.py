import io

from .File import JsonGet, JsonSet
from .OutputPlus import RedirectOutput


class TestPoints:
    class TestPoint:
        def __init__(self, input_args, except_result):
            self.input_args = input_args
            self.except_result = except_result

        def test(self, func):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with RedirectOutput(stdout, stderr):
                result = func(*self.input_args)
            return {
                "success": result == self.except_result,
                "result": result,
                "stdout": stdout.getvalue()
            }

    def __init__(self):
        self.points = []

    def add_point(self, input_args, except_result):
        self.points.append(self.TestPoint(input_args, except_result))

    def run(self, func):
        results = [point.test(func) for point in self.points]
        return {f"#{k}": v for k, v in zip(range(len(self.points)), results)}


class TestConfig:
    def __init__(self):
        self.name = None
        self.points = None
        self.timeout = None


class TestConfigReader:
    @staticmethod
    def read_config(filename):
        config = TestConfig()
        config_json = JsonGet(filename)

        config.name = config_json["name"]
        config.timeout = config_json["timeout"]

        config.points = TestPoints()

        for point in config_json["points"]:
            config.points.add_point(point["input"], point["except"])

        return config

    @staticmethod
    def write_config(config, filename):
        JsonSet(
            filename, **
            {
                "name": config.name,
                "timeout": config.timeout,
                "points": [{"input": point.input_args, "except": point.except_result} for point in config.points.points]
            })


def safe_test(test_config, func):
    pass
