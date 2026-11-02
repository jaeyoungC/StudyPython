"""리포지토리(repository) 계층: "할 일을 어디에 어떻게 저장하는가"를 서비스로부터 숨긴다.

TaskRepository 는 Protocol 입니다. 상속하지 않아도 같은 이름·시그니처의 메서드를 가진 객체라면
모두 TaskRepository 로 취급됩니다(구조적 타이핑, structural typing).

과제: 아래 세 클래스의 TODO 를 채우세요. Protocol 자체는 수정하지 않습니다.
- MemoryTaskRepository: self._tasks(TaskList) 에 위임. by_tag/search 는 all() 결과를 걸러서 만든다
  (search 는 대소문자 구분 없는 부분 문자열 포함).
- JsonTaskRepository: 메서드마다 _load() 로 TaskList 를 만들고, 바꾼 뒤에는 _save() 로 저장한다.
- SqliteTaskRepository: self._store(SqliteTaskStore) 에 그대로 위임한다. 이미 by_tag/search 가 있다.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Protocol

from .models import Task, TaskList
from .storage_json import JsonTaskStore
from .storage_sqlite import SqliteTaskStore


class TaskRepository(Protocol):
    """서비스가 저장소에 기대하는 것 전부. 여기 없는 메서드는 서비스가 쓸 수 없다."""

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task: ...
    def get(self, task_id: int) -> Task: ...  # 없으면 TaskNotFoundError
    def complete(self, task_id: int) -> Task: ...
    def remove(self, task_id: int) -> Task: ...
    def all(self) -> list[Task]: ...
    def open_tasks(self) -> list[Task]: ...
    def by_tag(self, tag: str) -> list[Task]: ...
    def search(self, text: str) -> list[Task]: ...


class MemoryTaskRepository:
    """TaskList 를 감싼 메모리 리포지토리. 테스트와 프로토타입에 쓴다."""

    def __init__(self) -> None:
        self._tasks = TaskList()

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def all(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def by_tag(self, tag: str) -> list[Task]:
        # TODO
        raise NotImplementedError

    def search(self, text: str) -> list[Task]:
        # TODO
        raise NotImplementedError


class JsonTaskRepository:
    """호출마다 파일 전체를 읽고 쓰는 단순한 구현. 느리지만 틀리기 어렵다."""

    def __init__(self, path: Path) -> None:
        self._store = JsonTaskStore(path)

    def _load(self) -> TaskList:
        return TaskList(self._store.load())

    def _save(self, tasks: TaskList) -> None:
        self._store.save(tasks.all())

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def all(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def by_tag(self, tag: str) -> list[Task]:
        # TODO
        raise NotImplementedError

    def search(self, text: str) -> list[Task]:
        # TODO
        raise NotImplementedError


class SqliteTaskRepository:
    """SqliteTaskStore 를 감싼 리포지토리. 검색은 FTS5 를 쓴다."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._store = SqliteTaskStore(conn)
        self._store.init_schema()

    def add(self, title: str, tags: Iterable[str] = (), due: date | None = None) -> Task:
        # TODO
        raise NotImplementedError

    def get(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def complete(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def remove(self, task_id: int) -> Task:
        # TODO
        raise NotImplementedError

    def all(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def open_tasks(self) -> list[Task]:
        # TODO
        raise NotImplementedError

    def by_tag(self, tag: str) -> list[Task]:
        # TODO
        raise NotImplementedError

    def search(self, text: str) -> list[Task]:
        # TODO
        raise NotImplementedError
