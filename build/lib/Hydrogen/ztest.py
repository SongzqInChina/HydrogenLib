import sys
import time
from io import StringIO
from types import FunctionType


# TODO: 完成HTML导出和JSON导出

class TestResult:
    def __init__(
            self, test_result, success, is_exception,
            elapsed_time, input_args, except_output, real_output, log
    ):
        self.test_result = test_result
        self.success = success
        self.is_exception = is_exception
        self.elapsed_time = elapsed_time
        self.input_args = input_args
        self.except_output = except_output
        self.real_output = real_output
        self.log = log

        self.is_success = self.success and not self.is_exception

    def to_dict(self):
        return {
            'success': self.success,
            'test_result': self.test_result,
            'is_exception': self.is_exception,
            'elapsed_time': self.elapsed_time,
            'input_args': self.input_args,
            'except_output': self.except_output,
            'real_output': self.real_output,
            'is_success': self.is_success
        }

    def __str__(self):
        return str(self.to_dict())

    __repr__ = __str__


class TestPoints:
    class TestPoint:
        def __init__(self, id, input_args=..., input_kwargs=..., except_output=None):
            if input_args is ...:
                input_args = ()
            if input_kwargs is ...:
                input_kwargs = {}
            self.except_output = except_output
            self.input_args = input_args
            self.input_kwargs = input_kwargs
            self.id = id

        def test(self, func):
            buffer = StringIO()
            sys.stdout = buffer
            try:
                time_start = time.time()
                res = func(*self.input_args, **self.input_kwargs)
                time_end = time.time()
                result = TestResult(
                    res, res == self.except_output, False,
                    (time_end - time_start), self.input_args, self.except_output, res, buffer.getvalue()
                )
            except Exception as e:
                result = TestResult(
                    e, False, True, 0, self.input_args, self.except_output,
                    None, buffer.getvalue()
                )

            sys.stdout = sys.__stdout__
            return result

    def __init__(self):
        TestPoint = self.TestPoint
        self.test_points: list[TestPoint] = []

    def add_point(self, input_args=..., input_kwargs=..., except_output=None):
        self.test_points.append(self.TestPoint(len(self.test_points), input_args, input_kwargs, except_output))

    def add_points(self, list_of_points: list[TestPoint]):
        self.test_points.extend(list_of_points)

    def test(self, func):
        results = [
            t.test(func) for t in self.test_points
        ]
        all_res = True
        for r in results:
            all_res = all_res and r.is_success
        #       最终结果  检查结果列表
        return all_res, results


class TestFunction:
    test_points: TestPoints

    def __init__(self, func, activate):
        self.doc = None
        self.name = func.__name__
        self.func = func
        self.activate = activate
        self.test_points = TestPoints()

    @property
    def length(self):
        return len(self.test_points.test_points)

    def add_point(self, input_args=..., input_kwargs=..., except_return_value=...):
        return self.test_points.add_point(input_args, input_kwargs, except_return_value)

    def add_points(self, list_of_points: list[TestPoints.TestPoint]):
        return self.test_points.add_points(list_of_points)

    def run(self):
        if not self.activate:
            raise Exception("The test function not Activate")
        tp = self.test_points.test(self.func)
        return {
            'success': tp[0],
            'test_results': tp[1]
        }


def test_function(activate: bool=True):
    def function_test(func: FunctionType):
        return TestFunction(func, activate)

    return function_test


def add_point(test_instance: TestFunction, input_args=..., input_kwargs=..., except_return_value=...):
    return test_instance.add_point(input_args, input_kwargs, except_return_value)


def add_points(test_instance: TestFunction, list_of_points: list[TestPoints.TestPoint]):
    return test_instance.add_points(list_of_points)


# 没有删除方法，移除添加语句就相当于删除了


def generate_html_report(tests: list[TestFunction], results: list[dict[str, list[TestResult] | None | bool]]):
    base_html = \
        """
        <!DOCTYPE html>
        <html lang="en">
            <meta charset="UTF-8">
            <title>{0}测试报告</title>
            <head>
                <style>
                    table, th, td {
                        border: 1px solid black;
                        border-collapse: collapse;
                    }
                    th, td {
                        padding: 15px;
                    }
                </style>
            </head>
            
            <body>
                <h1>测试报告</h1>
                <table>
                    <tr>
                        <th>测试名称</th>
                        <th>测试点</th>
                        <th>预期结果</th>
                        <th>实际结果</th>
                        <th>测试结果</th>
                    </tr>
                    <!-- 这里应该使用Python动态填充表格 -->
                    <tr>
                        {1}
                    </tr>
                </table>
            </body>
        </html>
        """
    html_table = ""
    for test, res in zip(tests, results):
        pass
