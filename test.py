from rich import print

from src.hydrolib.test_manager import *
from tests import test_funcs


def test_init():
    cc = ConfigCreator(".\\tests\\test_configs")
    test_names = {
        "class_namespace_namespace_test": {
            [
                [['a', 'b', 'c'], ['a', 'b', 'c'], {}],
                [['adasf', 'kajsl', 'jiew'], ['adasf', 'kajsl', 'jiew'], {}]
            ]
        },
        "class_auto_autos_test": {
            [
                [[]]
            ]
        }
    }


def main():
    Tm = TestManager()
    Tm.loads(".\\tests\\test_configs", "*.json")
    results = Tm.run(test_funcs)  # type: dict[str, Results]
    for key, res in results.items():
        for item in res:
            if item.success():
                print(f"[green]Success[/green]")
            else:
                if item.error is not None:
                    print(item.error)
                else:
                    print(item.ext_res, item.real_res)


if __name__ == '__main__':
    main()
