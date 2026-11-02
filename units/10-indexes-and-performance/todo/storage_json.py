"""JSON 파일 저장소 (07단원 완성본).

핵심은 두 가지다.

1. 원자적 쓰기(atomic write): 임시 파일에 다 쓴 뒤 `os.replace` 로 바꿔치기한다.
   쓰는 도중에 프로그램이 죽어도 원래 파일은 온전하다.
2. 깨진 파일은 조용히 넘기지 않고 StoreError 로 알린다. 원인 예외는 `raise ... from`
   으로 이어 붙여 트레이스백에서 볼 수 있게 한다.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Task


class StoreError(Exception):
    """저장소 파일을 읽거나 쓸 수 없을 때."""


class JsonTaskStore:
    """할 일 목록 전체를 JSON 파일 하나에 저장한다."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Task]:
        """파일을 읽어 Task 리스트로 돌려준다. 파일이 없으면 빈 리스트, 깨졌으면 StoreError."""
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise StoreError(f"{self.path} 을(를) JSON 으로 읽을 수 없습니다") from error
        if not isinstance(raw, list):
            raise StoreError(f"{self.path} 의 최상위는 리스트여야 합니다")
        try:
            return [Task.from_dict(item) for item in raw]
        except (KeyError, TypeError, ValueError) as error:
            raise StoreError(f"{self.path} 안의 할 일 형식이 잘못되었습니다") from error

    def save(self, tasks: list[Task]) -> None:
        """할 일 목록을 원자적으로 저장한다."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_name(self.path.name + ".tmp")
        data = [task.to_dict() for task in tasks]
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp_path, self.path)
