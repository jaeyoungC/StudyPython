"""명령줄 인터페이스 (06단원 완성본 + 07단원의 --file 저장 연결).

이 단원의 TODO 는 main() 안에만 있습니다.
"""

import argparse
import shlex
import sys
from pathlib import Path

from todo.models import Task, TaskList
from todo.storage_json import JsonTaskStore, StoreError

DEFAULT_FILE = "todo.json"


def format_task(task: Task) -> str:
    mark = "x" if task.done else " "
    return f"[{mark}] #{task.id} {task.title}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="할 일 관리")
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"저장 파일 (기본: {DEFAULT_FILE})")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="할 일 추가")
    add.add_argument("title", nargs="+", help="제목")

    done = subparsers.add_parser("done", help="완료 처리")
    done.add_argument("id", type=int)

    rm = subparsers.add_parser("rm", help="삭제")
    rm.add_argument("id", type=int)

    ls = subparsers.add_parser("ls", help="목록")
    ls.add_argument("--open", action="store_true", help="미완료만")

    subparsers.add_parser("shell", help="대화형 모드")
    return parser


def run_command(args: argparse.Namespace, tasks: TaskList) -> int:
    try:
        if args.command == "add":
            task = tasks.add(" ".join(args.title))
            print(f"추가: #{task.id} {task.title}")
        elif args.command == "done":
            task = tasks.complete(args.id)
            print(f"완료: #{task.id} {task.title}")
        elif args.command == "rm":
            task = tasks.remove(args.id)
            print(f"삭제: #{task.id} {task.title}")
        elif args.command == "ls":
            for task in tasks.open_tasks() if args.open else tasks.all():
                print(format_task(task))
        return 0
    except ValueError as error:
        print(f"오류: {error}", file=sys.stderr)
        return 1


def run_shell(tasks: TaskList, after_each: "callable | None" = None) -> int:
    """after_each: 명령이 성공할 때마다 부르는 함수 (07단원: 저장)."""
    parser = build_parser()
    while True:
        try:
            line = input("todo> ").strip()
        except EOFError:
            break
        if not line:
            continue
        if line in ("quit", "exit"):
            break
        try:
            args = parser.parse_args(shlex.split(line))
        except SystemExit:
            continue
        if args.command == "shell":
            continue
        if run_command(args, tasks) == 0 and after_each is not None:
            after_each()
    return 0


def main(argv: list[str] | None = None, tasks: TaskList | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = JsonTaskStore(Path(args.file))

    if tasks is None:
        # TODO 1: store.load() 로 TaskList 를 채우세요.
        #         StoreError 가 나면 "오류: ..." 를 stderr 에 쓰고 1 을 돌려줍니다.
        raise NotImplementedError

    def save() -> None:
        store.save(tasks.all())

    if args.command == "shell":
        # TODO 2: 명령이 성공할 때마다 저장되도록 run_shell 에 save 를 넘기세요.
        raise NotImplementedError

    code = run_command(args, tasks)
    # TODO 3: 성공(0)했고 목록을 바꾸는 명령(add/done/rm)이었으면 save()
    raise NotImplementedError
