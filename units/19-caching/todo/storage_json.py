"""JSON 파일 저장소 (07단원). 임시 파일에 쓴 뒤 os.replace 로 원자적으로 교체한다."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Task


class StoreError(Exception):
    """파일이 깨졌거나 읽을 수 없을 때."""


class JsonTaskStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Task]:
        """파일이 없으면 [], 깨졌으면 StoreError."""
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [Task.from_dict(item) for item in raw]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            raise StoreError(f"{self.path} 을(를) 읽을 수 없습니다: {error}") from error

    def save(self, tasks: list[Task]) -> None:
        """같은 디렉터리의 임시 파일에 쓴 뒤 교체한다. 중간에 죽어도 원본은 남는다."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        payload = json.dumps([t.to_dict() for t in tasks], ensure_ascii=False, indent=2)
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, self.path)
