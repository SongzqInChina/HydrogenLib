import argparse
import os
import subprocess
import sys
import time
import HydrogenLib
import rich.traceback
from rich import print

rich.traceback.install()


def run_command(command):
    ps = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ps.returncode, ps


def init_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--install", '-i',
        help="Install Module",
        action="store_true"
    )
    parser.add_argument(
        "--skip-check", '-c',
        help="Skip check Module wheel",
        action="store_true"
    )
    parser.add_argument(
        "--skip-upload", '-d',
        help="Skip upload Module wheel",
        action="store_true"
    )
    parser.add_argument(
        '--skip-build', '-s',
        help="Skip building Module wheel",
        action="store_true"
    )
    parser.add_argument(
        "--clean", '-k',
        help="Clean Module wheel",
        action="store_true"
    )
    parser.add_argument(  # 接收一个参数，version
        "--version", '-v',
        help="Set module version",
        default="None",
        type=str
    )
    parser.add_argument(
        "--name", '-n',
        help="Set print name",
        default="Module",
        type=str
    )
    parser.add_argument(
        "--path", '-p',
        help="Version file path",
        default=".\\version",
        type=str
    )


parser = argparse.ArgumentParser()
init_parser(parser)

args = parser.parse_args(sys.argv[1:])

version_path = args.path
name = args.name


if __name__ == '__main__':
    console = rich.console.Console(force_terminal=True)
    spinner = "aesthetic"

    if args.version != "None":
        with open(version_path, "r") as f:
            f.seek(0)
            cur_version = tuple(map(int, f.read().strip().split('.')))
        now_version = tuple(map(int, args.version.strip().split('.')))
        if cur_version >= now_version:
            console.print("[bold red]The version you set is lower than the current version!")
        else:
            with console.status("Setting Module version...", spinner=spinner):
                rt_code, ps = run_command(["hatch", "version", args.version])
                with open(version_path, "w") as f:
                    f.write(args.version)
            time.sleep(0.1)
            if rt_code != 0:
                console.print("[bold red]Setting Module version failed!")
                console.print(ps.stderr.decode())
                console.print(ps.stdout.decode())
                sys.exit(rt_code)
            print("[bold green]success!")
    if args.clean:
        if os.name == 'nt':
            command = ["powershell.exe", "-Command", "rm", r".\dist\*"]
        elif os.name == 'posix':
            command = ["rm", "-rf", r"./dist/*"]
        else:
            console.print(f"[bold red]Unsupported OS({os.name})!")
            sys.exit(1)

        with console.status("Cleaning Module wheel...", spinner=spinner):
            rt_code, ps = run_command(command)
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]Cleaning Module wheel failed!")
            console.print(ps.stderr)
            console.print(ps.stdout)
            sys.exit(rt_code)
        print("[bold green]success!")

    if not args.skip_build:
        # 播放工作动画
        with console.status("Building Module wheel...", spinner=spinner):
            rt_code, ps = run_command(["hatch", "build"])
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]Building Module wheel failed!")
            console.print(ps.stderr)
            sys.exit(rt_code)
        print("[bold green]success!")
    # console.console.print('\n')
    if not args.skip_check:
        with console.status("Checking Module wheel...", spinner=spinner):
            rt_code, ps = run_command(["twine", "check", "dist/*"])
        time.sleep(0.1)
        if rt_code != 0:
            console.print("[bold red]Checking Module wheel failed!")
            console.print(ps.stderr)
            sys.exit(rt_code)
        print("[bold green]success!")
    # console.console.print('\n')
    if not args.skip_upload:
        with console.status("Uploading Module wheel...", spinner=spinner):
            rt_code, ps = run_command(["twine", "upload", r".\dist\*", '--disable-progress-bar'])
        time.sleep(0.1)
        if rt_code != 0:
            console.print(f"[bold red]failed!({rt_code})")
            console.print(ps.stdout.decode())
            console.print(ps.stderr.decode())
            sys.exit(rt_code)
        print("[bold green]success!")

    print("[bold green]all steps are success, you can run `pip install Module -U` to update Module")
