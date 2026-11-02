"""43단원: 할 일 기능을 에이전트가 호출할 도구로 노출한다.

세 도구(list_tasks / add_task / complete_task)는 **순수 함수**로 먼저 만들고,
`build_server()`가 그 함수를 MCP(Model Context Protocol) 서버에 등록합니다.
테스트는 순수 함수만 검사합니다. 서버는 과제 C에서 손으로 확인합니다.

실제 프로젝트에서는 이 파일을 `todo/mcp_server.py`로 옮기고 `repo`에
`SqliteTaskRepository`를 주입하세요. 여기서는 단원 폴더를 독립적으로 두기 위해
최소한의 `_InMemoryRepo`를 함께 둡니다.

MCP Python SDK 설치: `pip install "mcp[cli]"` (테스트에는 필요 없습니다)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

MAX_LIMIT = 50
DEFAULT_LIMIT = 20


# ---------------------------------------------------------------------------
# 도메인 (docs/project-api.md 와 같은 이름)
# ---------------------------------------------------------------------------


class TaskNotFoundError(ValueError):
    """없는 id."""


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    tags: list[str] = field(default_factory=list)
    due: date | None = None


class TaskRepository(Protocol):
    """15단원 Protocol 중 이 단원에서 쓰는 부분만."""

    def add(self, title: str, tags: tuple[str, ...] = ()) -> Task: ...
    def get(self, task_id: int) -> Task: ...
    def complete(self, task_id: int) -> Task: ...
    def all(self) -> list[Task]: ...


class _InMemoryRepo:
    """테스트 전용 최소 구현. 규칙(빈 제목·중복 완료)은 서비스 계층의 것이지만,
    이 단원 폴더에는 서비스가 없으므로 여기서 같은 규칙을 지킵니다."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, title: str, tags: tuple[str, ...] = ()) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("제목이 비어 있습니다")
        task = Task(id=self._next_id, title=title, tags=list(tags))
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(f"할 일 {task_id} 없음") from None

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if task.done:
            raise ValueError("이미 완료된 할 일입니다")
        task.done = True
        return task

    def all(self) -> list[Task]:
        return list(self._tasks.values())


# ---------------------------------------------------------------------------
# 도구 결과 형식: API 오류 형식 {"error": {"code", "message"}} 과 통일
# ---------------------------------------------------------------------------


def _ok(**payload: Any) -> dict[str, Any]:
    return {"ok": True, **payload}


def _error(code: str, message: str) -> dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}}


def _public(task: Task) -> dict[str, Any]:
    """모델에게 보여 줄 최소 필드. 창(context window)을 아끼기 위해 태그·버전 등은 뺀다."""
    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
        "due": task.due.isoformat() if task.due else None,
    }


# ---------------------------------------------------------------------------
# 도구 (순수 함수)
# ---------------------------------------------------------------------------


def list_tasks(
    repo: TaskRepository,
    done: bool | None = None,
    limit: int = DEFAULT_LIMIT,
    cursor: int | None = None,
) -> dict[str, Any]:
    """할 일 목록을 돌려준다.

    - done=None 이면 전체, True/False 면 그 상태만
    - limit 은 1..MAX_LIMIT 으로 자른다 (0 이하 → 1, 50 초과 → 50)
    - cursor 는 "이 id 보다 큰 것부터" (17단원 커서 페이지네이션). 다음 페이지가 없으면 next_cursor=None
    - 반환: {"ok": True, "items": [_public(task), ...], "next_cursor": int | None}
    """
    # TODO
    raise NotImplementedError


def add_task(
    repo: TaskRepository,
    title: str,
    idempotency_key: str | None = None,
    keys: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """할 일을 추가한다.

    - keys 는 멱등성 저장소(26단원). idempotency_key 가 keys 에 있으면 저장된 결과를 **그대로** 돌려주고
      repo 에는 아무것도 추가하지 않는다. 없으면 추가한 뒤 결과를 keys 에 저장한다
    - 빈 제목(공백만)은 repo.add 가 ValueError 를 던진다 → {"ok": False, "error": {"code": "invalid_title", ...}}
    - 성공: {"ok": True, "task": _public(task)}
    """
    # TODO
    raise NotImplementedError


def complete_task(repo: TaskRepository, task_id: int) -> dict[str, Any]:
    """할 일을 완료 처리한다.

    - 없는 id: code "not_found"
    - 이미 완료: code "already_done" (HTTP 409 와 같은 의미)
    - 성공: {"ok": True, "task": _public(task)}
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# 도구 설명: 모델의 창에 들어가므로 짧고 정확하게
# ---------------------------------------------------------------------------


def tool_descriptions() -> dict[str, str]:
    """도구 이름 → 설명. 세 설명의 길이 합이 400자를 넘지 않게 쓴다.

    힌트: "무엇을 하는가 + 언제 쓰는가 + 돌려주는 것" 세 조각이면 충분합니다.
    """
    # TODO
    raise NotImplementedError


# ---------------------------------------------------------------------------
# MCP 서버: 얇은 껍데기. 규칙은 넣지 않는다.
# ---------------------------------------------------------------------------


def build_server(repo: TaskRepository, read_only: bool = False):
    """FastMCP 서버를 만들어 돌려준다. read_only=True 면 list_tasks 만 등록한다.

    MCP Python SDK 의 관례:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("todo")
        @mcp.tool(description=...)
        def list_tasks(done: bool | None = None, limit: int = 20, cursor: int | None = None) -> dict: ...

    등록하는 함수는 repo 를 인자로 받지 않도록 클로저로 감싸세요 (모델은 repo 를 모릅니다).
    `mcp` 패키지는 여기서만 import 해서, 설치하지 않아도 테스트가 돌게 합니다.
    """
    from mcp.server.fastmcp import FastMCP  # 지연 import: 테스트에는 불필요

    descriptions = tool_descriptions()
    mcp = FastMCP("todo")

    @mcp.tool(name="list_tasks", description=descriptions["list_tasks"])
    def _list(done: bool | None = None, limit: int = DEFAULT_LIMIT, cursor: int | None = None) -> dict:
        return list_tasks(repo, done=done, limit=limit, cursor=cursor)

    if not read_only:
        keys: dict[str, dict[str, Any]] = {}

        @mcp.tool(name="add_task", description=descriptions["add_task"])
        def _add(title: str, idempotency_key: str | None = None) -> dict:
            return add_task(repo, title, idempotency_key=idempotency_key, keys=keys)

        @mcp.tool(name="complete_task", description=descriptions["complete_task"])
        def _complete(task_id: int) -> dict:
            return complete_task(repo, task_id)

    return mcp


if __name__ == "__main__":
    # 과제 C: `python mcp_tools.py` 로 stdio 서버를 띄우고 Claude Code 에 MCP 서버로 등록해 보세요.
    # 개발용 메모리 저장소이므로 서버를 끄면 데이터는 사라집니다.
    build_server(_InMemoryRepo()).run()
