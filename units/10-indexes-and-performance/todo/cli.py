"""명령줄 인터페이스 (06~07단원 완성본).

사용법: python -m todo [--file todo.json] <명령>
  add <제목> [--tag t ...]  할 일 추가
  done <id>    완료 처리
  rm <id>      삭제
  ls [--open] [--tag t]     목록 (--open: 미완료만, --tag: 태그로 거르기)

종료 코드: 성공 0, 사용자 오류(빈 제목, 없는 id, 잘못된 인자) 1.
`main(argv)` 가 인자를 직접 받으므로 테스트에서 `main(["add", "x"])` 처럼 호출할 수 있다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import TaskList
from .storage_json import JsonTaskStore, StoreError

DEFAULT_FILE = Path("todo.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="할 일 관리")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="저장 파일 (기본: todo.json)")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="할 일 추가")
    add.add_argument("title", help="제목")
    add.add_argument("--tag", action="append", default=[], help="태그 (여러 번 지정 가능)")

    done = commands.add_parser("done", help="완료 처리")
    done.add_argument("id", type=int)

    remove = commands.add_parser("rm", help="삭제")
    remove.add_argument("id", type=int)

    ls = commands.add_parser("ls", help="목록")
    ls.add_argument("--open", action="store_true", help="미완료만 보기")
    ls.add_argument("--tag", help="이 태그가 붙은 것만 보기")
    return parser


def format_task(task) -> str:
    mark = "x" if task.done else " "
    tags = f"  [{', '.join(task.tags)}]" if task.tags else ""
    return f"[{mark}] #{task.id} {task.title}{tags}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exit_:  # argparse 는 잘못된 인자에 exit(2), --help 에 exit(0) 을 쓴다
        return 0 if exit_.code == 0 else 1

    store = JsonTaskStore(args.file)
    try:
        tasks = TaskList(store.load())
        if args.command == "add":
            task = tasks.add(args.title, tags=args.tag)
            print(f"추가: {format_task(task)}")
        elif args.command == "done":
            task = tasks.complete(args.id)
            print(f"완료: {format_task(task)}")
        elif args.command == "rm":
            task = tasks.remove(args.id)
            print(f"삭제: {format_task(task)}")
        elif args.command == "ls":
            shown = tasks.by_tag(args.tag) if args.tag else tasks.all()
            if args.open:
                shown = [task for task in shown if not task.done]
            for task in shown:
                print(format_task(task))
            return 0
        store.save(tasks.all())
    except (ValueError, StoreError) as error:  # TaskNotFoundError 도 ValueError 다
        print(f"오류: {error}", file=sys.stderr)
        return 1
    return 0
