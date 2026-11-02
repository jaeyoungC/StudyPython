"""1주차: 메모리에만 저장하는 할 일 목록.

할 일 하나는 {"id": int, "title": str, "done": bool} 형태의 딕셔너리입니다.
각 함수의 TODO를 채워 `pytest weeks/week01` 을 통과시키세요.
"""


def add_task(tasks: list[dict], title: str) -> dict:
    """새 할 일을 tasks 끝에 추가하고, 추가한 할 일을 반환한다.

    - id는 기존 할 일 중 가장 큰 id + 1 (목록이 비어 있으면 1)
    - title의 앞뒤 공백은 제거한다
    - 공백을 제거한 title이 비어 있으면 ValueError
    """
    # TODO
    raise NotImplementedError


def find_task(tasks: list[dict], task_id: int) -> dict:
    """id가 task_id인 할 일을 반환한다. 없으면 ValueError."""
    # TODO
    raise NotImplementedError


def complete_task(tasks: list[dict], task_id: int) -> dict:
    """할 일을 완료 상태(done=True)로 바꾸고 반환한다. 없으면 ValueError.

    힌트: find_task를 재사용하세요.
    """
    # TODO
    raise NotImplementedError


def remove_task(tasks: list[dict], task_id: int) -> dict:
    """할 일을 tasks에서 지우고, 지운 할 일을 반환한다. 없으면 ValueError."""
    # TODO
    raise NotImplementedError


def list_tasks(tasks: list[dict], only_open: bool = False) -> list[dict]:
    """할 일 목록을 새 리스트로 반환한다. only_open=True면 done=False인 것만."""
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 아래는 직접 실행해 볼 수 있는 간단한 CLI입니다. 수정하지 않아도 됩니다.
# ---------------------------------------------------------------------------

HELP = "명령: add <제목> | done <id> | rm <id> | ls | open | quit"


def main() -> None:
    tasks: list[dict] = []
    print(HELP)
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        command, _, arg = line.partition(" ")
        try:
            if command == "add":
                task = add_task(tasks, arg)
                print(f"추가: #{task['id']} {task['title']}")
            elif command == "done":
                complete_task(tasks, int(arg))
            elif command == "rm":
                remove_task(tasks, int(arg))
            elif command in ("ls", "open"):
                for task in list_tasks(tasks, only_open=(command == "open")):
                    mark = "x" if task["done"] else " "
                    print(f"[{mark}] #{task['id']} {task['title']}")
            elif command == "quit":
                break
            else:
                print(HELP)
        except ValueError as error:
            print(f"오류: {error}")


if __name__ == "__main__":
    main()
