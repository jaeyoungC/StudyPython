"""JSON 파일 저장소. TODO를 채워 `pytest units/07-json-store` 를 통과시키세요."""

import json
import os
from pathlib import Path

from todo.models import Task


class StoreError(Exception):
    """저장 파일을 읽을 수 없을 때 (깨진 JSON, 잘못된 구조, 잘못된 항목)."""


class JsonTaskStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Task]:
        """파일에서 할 일 목록을 읽는다.

        - 파일이 없으면 []
        - JSON 이 깨졌거나(json.JSONDecodeError), 최상위가 리스트가 아니거나,
          항목이 Task.from_dict 를 통과하지 못하면(ValueError) StoreError
          → 원인을 잃지 않도록 `raise StoreError(...) from error`
        """
        # TODO
        raise NotImplementedError

    def save(self, tasks: list[Task]) -> None:
        """할 일 목록을 JSON 으로 원자적으로 저장한다.

        1. [task.to_dict() for task in tasks] 를 json.dumps(ensure_ascii=False, indent=2)
        2. self.path 와 같은 폴더의 임시 파일(예: self.path.with_suffix(".tmp"))에 먼저 쓴다
        3. os.replace(임시 파일, self.path)
        직렬화나 쓰기에서 예외가 나면 원본 파일은 그대로여야 하고, 임시 파일은 남기지 않는다.
        """
        # TODO
        raise NotImplementedError
