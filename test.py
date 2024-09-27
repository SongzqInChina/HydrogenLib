from tests import test_funcs
from rich import print


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
