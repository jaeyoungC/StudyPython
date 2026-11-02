"""3주차: 할 일을 JSON 파일에 저장하고 불러오기.

할 일 하나는 1주차와 같은 {"id": int, "title": str, "done": bool} 딕셔너리입니다.
TODO를 채워 `pytest weeks/week03` 을 통과시키세요.
"""

import json
import os
from pathlib import Path


class StoreError(Exception):
    """저장 파일을 읽을 수 없을 때 발생한다."""


def save_tasks(path: Path, tasks: list[dict]) -> None:
    """tasks를 JSON으로 path에 저장한다.

    - 한글이 \\uXXXX 로 바뀌지 않게 저장한다 (ensure_ascii=False)
    - 원자적으로 쓴다: path와 같은 폴더의 임시 파일(예: path.with_suffix(".json.tmp"))에
      먼저 다 쓴 뒤 os.replace(임시파일, path)
    """
    # TODO
    raise NotImplementedError


def load_tasks(path: Path) -> list[dict]:
    """path에서 할 일 목록을 읽어 반환한다.

    - 파일이 없으면 빈 리스트
    - JSON이 깨졌거나 최상위 값이 리스트가 아니면 StoreError
      (원래 예외를 잃지 않도록 `raise StoreError(...) from error`)
    """
    # TODO
    raise NotImplementedError
