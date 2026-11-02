"""할 일 관리 패키지 (16단원까지의 완성본).

- models.py        Task, TaskNotFoundError, TaskList (메모리)
- storage_json.py  JSON 파일 저장 (원자적 쓰기)
- storage_sqlite.py SQLite 저장 (태그, 마이그레이션, FTS5 검색, 감사 로그)
- repository.py    TaskRepository Protocol 과 Memory/Json/Sqlite 구현
- service.py       TaskService: 업무 규칙, 시계 주입
- simple_http.py   http.server 만으로 만든 최소 HTTP 서버 (프레임워크 없음)
- cli.py           argparse 기반 명령줄 진입점
"""

from .models import Task, TaskList, TaskNotFoundError

__all__ = ["Task", "TaskList", "TaskNotFoundError"]
