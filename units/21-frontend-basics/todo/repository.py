"""리포지토리(repository) 계층: "할 일을 어디에 어떻게 저장하는가"를 서비스로부터 숨긴다.

TaskRepository 는 Protocol 입니다. 상속하지 않아도 같은 이름·시그니처의 메서드를 가진 객체라면
모두 TaskRepository 로 취급됩니다(구조적 타이핑, structural typing).
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

    def add(
        self, title: str, tags: Iterable[str] = (), due: date | None = None, owner_id: int | None = None
    ) -> Task: ...
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

    def add(
        self, title: str, tags: Iterable[str] = (), due: date | None = None, owner_id: int | None = None
    ) -> Task:
        return self._tasks.add(title, tags=list(tags), due=due, owner_id=owner_id)

    def get(self, task_id: int) -> Task:
        return self._tasks.get(task_id)

    def complete(self, task_id: int) -> Task:
        return self._tasks.complete(task_id)

    def remove(self, task_id: int) -> Task:
        return self._tasks.remove(task_id)

    def all(self) -> list[Task]:
        return self._tasks.all()

    def open_tasks(self) -> list[Task]:
        return self._tasks.open_tasks()

    def by_tag(self, tag: str) -> list[Task]:
        return [t for t in self._tasks.all() if tag in t.tags]

    def search(self, text: str) -> list[Task]:
        needle = text.strip().lower()
        return [t for t in self._tasks.all() if needle and needle in t.title.lower()]


class JsonTaskRepository:
    """호출마다 파일 전체를 읽고 쓰는 단순한 구현. 느리지만 틀리기 어렵다."""

    def __init__(self, path: Path) -> None:
        self._store = JsonTaskStore(path)

    def _load(self) -> TaskList:
        return TaskList(self._store.load())

    def _save(self, tasks: TaskList) -> None:
        self._store.save(tasks.all())

    def add(
        self, title: str, tags: Iterable[str] = (), due: date | None = None, owner_id: int | None = None
    ) -> Task:
        tasks = self._load()
        task = tasks.add(title, tags=list(tags), due=due, owner_id=owner_id)
        self._save(tasks)
        return task

    def get(self, task_id: int) -> Task:
        return self._load().get(task_id)

    def complete(self, task_id: int) -> Task:
        tasks = self._load()
        task = tasks.complete(task_id)
        self._save(tasks)
        return task

    def remove(self, task_id: int) -> Task:
        tasks = self._load()
        task = tasks.remove(task_id)
        self._save(tasks)
        return task

    def all(self) -> list[Task]:
        return self._load().all()

    def open_tasks(self) -> list[Task]:
        return self._load().open_tasks()

    def by_tag(self, tag: str) -> list[Task]:
        return [t for t in self._load().all() if tag in t.tags]

    def search(self, text: str) -> list[Task]:
        needle = text.strip().lower()
        return [t for t in self._load().all() if needle and needle in t.title.lower()]


class SqliteTaskRepository:
    """SqliteTaskStore 를 감싼 리포지토리. 검색은 FTS5 를 쓴다."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._store = SqliteTaskStore(conn)
        self._store.init_schema()

    def add(
        self, title: str, tags: Iterable[str] = (), due: date | None = None, owner_id: int | None = None
    ) -> Task:
        return self._store.add(title, tags=tags, due=due, owner_id=owner_id)

    def get(self, task_id: int) -> Task:
        return self._store.get(task_id)

    def complete(self, task_id: int) -> Task:
        return self._store.complete(task_id)

    def remove(self, task_id: int) -> Task:
        return self._store.remove(task_id)

    def all(self) -> list[Task]:
        return self._store.all()

    def open_tasks(self) -> list[Task]:
        return self._store.open_tasks()

    def by_tag(self, tag: str) -> list[Task]:
        return self._store.by_tag(tag)

    def search(self, text: str) -> list[Task]:
        return self._store.search(text)
