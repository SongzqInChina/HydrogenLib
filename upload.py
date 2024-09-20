import argparse
import subprocess
import sys
import time

from rich import print
import rich.traceback
import rich.spinner

rich.traceback.install()


def run_command(command):
    ps = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ps.returncode, ps


args = sys.argv[1::]


def init_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--install", '-i',
        help="Install HydrogenLib",
        action="store_true"
    )
    parser.add_argument(
        "--skip-check", '-c',
        help="Skip check HydrogenLib wheel",
        action="store_true"
    )
    parser.add_argument(
        "--skip-upload", '-d',
        help="Skip upload HydrogenLib wheel",
        action="store_true"
    )
    parser.add_argument(
        '--skip-build', '-s',
        help="Skip building HydrogenLib wheel",
        action="store_true"
    )


if __name__ == '__main__':
    spinner = "aesthetic"
    parser = argparse.ArgumentParser()
    console = rich.console.Console(force_terminal=True)
    init_parser(parser)
    args = parser.parse_args(args)
    if not args.skip_build:
        # 播放工作动画
        with console.status("Building HydrogenLib wheel...", spinner=spinner):
            rt_code, ps = run_command(["hatch", "build"])
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]Building HydrogenLib wheel failed!")
            console.print(ps.stderr)
            sys.exit(rt_code)
        print("[bold green]success!")
    # console.console.print('\n')
    if not args.skip_check:
        with console.status("Checking HydrogenLib wheel...", spinner=spinner):
            rt_code, ps = run_command(["twine", "check", "dist/*"])
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]Checking HydrogenLib wheel failed!")
            console.print(ps.stderr)
            sys.exit(rt_code)
        print("[bold green]success!")
    # console.console.print('\n')
    if not args.skip_upload:
        with console.status("Uploading HydrogenLib wheel...", spinner=spinner):
            rt_code, ps = run_command(["twine", "upload", "dist/*"])
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]failed!")
            console.print(ps.stdout.decode())
            sys.exit(rt_code)
        print("[bold green]success!")

    if args.install:
        with console.status("Installing HydrogenLib...", spinner=spinner):
            rt_code, ps = run_command(["pip", "install", "HydrogenLib", '-u'])
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]failed!")
            console.print(ps.stdout.decode('utf-8'))
            sys.exit(rt_code)
        print("[bold green]success!")
    input()



