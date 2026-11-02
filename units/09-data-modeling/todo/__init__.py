"""할 일 관리 프로그램 `todo` 패키지.

03단원에서 시작한 프로그램이 단원을 거치며 자랍니다. 이 패키지는 07단원까지의 완성본에
이번 단원이 새로 만드는 모듈을 더한 것입니다. 각 모듈의 역할:

- models.py        : 도메인 모델 Task, TaskList, TaskNotFoundError
- storage_json.py  : JSON 파일 저장(원자적 쓰기)
- storage_sqlite.py: SQLite 저장 (08단원), 태그 테이블 (09단원)
- cli.py           : argparse 기반 명령줄 인터페이스
"""

from .models import Task, TaskList, TaskNotFoundError, normalize_tags
from .storage_json import JsonTaskStore, StoreError

__all__ = ["Task", "TaskList", "TaskNotFoundError", "normalize_tags", "JsonTaskStore", "StoreError"]
