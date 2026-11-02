"""명령줄 인터페이스. TODO를 채워 `pytest units/06-package-and-cli` 를 통과시키세요.

설계 원칙
- main(argv, tasks) -> int : 종료 코드를 돌려준다. sys.exit 는 __main__.py 에서만.
- 정상 출력은 print, 오류는 print(..., file=sys.stderr) 와 return 1.
"""

import argparse
import sys

from todo.models import Task, TaskList


def format_task(task: Task) -> str:
    """'[ ] #1 산책' 또는 '[x] #1 산책'"""
    # TODO
    raise NotImplementedError


def build_parser() -> argparse.ArgumentParser:
    """하위 명령 add / done / rm / ls / shell 을 가진 파서.

    - add: 위치 인자 title (여러 단어를 허용하려면 nargs="+" 로 받아 " ".join)
    - done, rm: 위치 인자 id (type=int)
    - ls: 옵션 --open (store_true)
    - shell: 인자 없음
    """
    parser = argparse.ArgumentParser(prog="todo", description="할 일 관리")
    subparsers = parser.add_subparsers(dest="command", required=True)
    # TODO: 하위 명령 다섯 개를 추가하세요
    return parser


def run_command(args: argparse.Namespace, tasks: TaskList) -> int:
    """파싱된 인자 하나를 실행한다. 성공 0, 사용자 오류(ValueError 계열) 1."""
    # TODO
    # 힌트: try 안에서 args.command 에 따라 분기하고, except ValueError as error: 에서
    #       print(f"오류: {error}", file=sys.stderr) 후 return 1
    raise NotImplementedError


def run_shell(tasks: TaskList) -> int:
    """'quit' 를 입력할 때까지 한 줄씩 읽어 run_command 로 실행한다.

    힌트: shlex.split(line) 으로 따옴표 있는 입력을 나누고, build_parser().parse_args(...) 로 파싱.
    argparse 가 잘못된 입력에 SystemExit 를 던지므로 except SystemExit: 로 받아 계속 진행.
    """
    # TODO
    raise NotImplementedError


def main(argv: list[str] | None = None, tasks: TaskList | None = None) -> int:
    if tasks is None:
        tasks = TaskList()
    args = build_parser().parse_args(argv)
    if args.command == "shell":
        return run_shell(tasks)
    return run_command(args, tasks)
