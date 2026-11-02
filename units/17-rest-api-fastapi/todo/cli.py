"""명령줄 진입점 (06·07단원). 기본 저장소는 JSON 파일이다.

명령: add <제목> [--tag T ...] | done <id> | rm <id> | ls [--open]
종료 코드: 성공 0, 사용자 오류 1
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .models import TaskList
from .storage_json import JsonTaskStore, StoreError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="할 일 관리")
    parser.add_argument("--file", type=Path, default=Path("todo.json"), help="저장 파일 (기본 todo.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="할 일 추가")
    p_add.add_argument("title")
    p_add.add_argument("--tag", action="append", default=[], help="태그 (여러 번 가능)")

    sub.add_parser("done", help="완료 처리").add_argument("id", type=int)
    sub.add_parser("rm", help="삭제").add_argument("id", type=int)
    p_ls = sub.add_parser("ls", help="목록")
    p_ls.add_argument("--open", action="store_true", help="미완료만")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = JsonTaskStore(args.file)
    try:
        tasks = TaskList(store.load())
        if args.command == "add":
            task = tasks.add(args.title, tags=args.tag)
            print(f"추가: #{task.id} {task.title}")
        elif args.command == "done":
            tasks.complete(args.id)
        elif args.command == "rm":
            tasks.remove(args.id)
        elif args.command == "ls":
            for task in tasks.open_tasks() if args.open else tasks.all():
                mark = "x" if task.done else " "
                tags = f" [{', '.join(task.tags)}]" if task.tags else ""
                due = f" (~{task.due})" if task.due else ""
                print(f"[{mark}] #{task.id} {task.title}{tags}{due}")
            return 0
        store.save(tasks.all())
        return 0
    except (ValueError, StoreError) as error:
        print(f"오류: {error}")
        return 1
