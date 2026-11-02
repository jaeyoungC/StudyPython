"""할 일 관리 패키지 (20단원까지의 완성본).

- models.py        Task, TaskNotFoundError, TaskList (메모리)
- storage_json.py  JSON 파일 저장 (원자적 쓰기)
- storage_sqlite.py SQLite 저장 (태그, 마이그레이션, FTS5 검색, 감사 로그)
- repository.py    TaskRepository Protocol 과 Memory/Json/Sqlite 구현
- service.py       TaskService: 업무 규칙, 시계 주입
- simple_http.py   http.server 만으로 만든 최소 HTTP 서버 (프레임워크 없음)
- schemas.py       HTTP 경계의 Pydantic 모델
- api.py           FastAPI 앱 팩토리 create_app(service, users)
- auth.py          비밀번호 해싱, 토큰, UserStore (18단원)
- cache.py         MemoryCache: 서비스 계층 목록 캐시 (19단원)
- events.py, notifier.py, worker.py, async_demo.py  이벤트·알림 워커·asyncio 연습 (20단원)
- cli.py           argparse 기반 명령줄 진입점
"""

from .models import Task, TaskList, TaskNotFoundError

__all__ = ["Task", "TaskList", "TaskNotFoundError"]
