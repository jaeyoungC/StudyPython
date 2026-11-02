# 공통 프로젝트 명세 — "할 일 관리" 프로그램의 단계별 모습

모든 단원은 같은 프로그램을 키웁니다. 단원 작성자(사람이든 AI든)는 이 명세를 지켜야 학습자가 단원을 옮겨도
이름이 바뀌지 않습니다. 06단원부터 각 단원 폴더에는 **앞 단원까지의 완성본 `todo/` 패키지**가 들어 있고,
그 단원에서 새로 만드는 부분에만 `TODO` 가 있습니다. (06: `models.py` 완성본 + `cli.py` TODO, 07: `cli.py` 완성본 + `storage_json.py` TODO)

## 도메인

```python
@dataclass
class Task:
    id: int
    title: str          # 앞뒤 공백 제거, 빈 문자열 금지 (ValueError)
    done: bool = False
    # 09단원부터: tags: list[str] = field(default_factory=list)
    # 12단원부터: due: date | None = None

class TaskNotFoundError(ValueError): ...   # 없는 id
```

## 05단원 이후 — `todo/models.py`

```python
class TaskList:                      # 메모리 저장
    def add(self, title: str) -> Task
    def get(self, task_id: int) -> Task          # 없으면 TaskNotFoundError
    def complete(self, task_id: int) -> Task     # 이미 완료면 ValueError
    def remove(self, task_id: int) -> Task
    def all(self) -> list[Task]                  # 새 리스트
    def open_tasks(self) -> list[Task]           # done=False만, 새 리스트
    def __len__(self) -> int
```

## 06단원 이후 — 패키지 구조

```
todo/
  __init__.py
  __main__.py      # python -m todo
  models.py        # Task, TaskNotFoundError, TaskList
  cli.py           # main(argv: list[str] | None = None) -> int, argparse
```

CLI 명령: `add <제목>`, `done <id>`, `rm <id>`, `ls [--open]`. 종료 코드: 성공 0, 사용자 오류 1.

## 07단원 이후 — `todo/storage_json.py`

```python
class JsonTaskStore:
    def __init__(self, path: Path)
    def load(self) -> list[Task]        # 없으면 [], 깨졌으면 StoreError
    def save(self, tasks: list[Task]) -> None   # 원자적 쓰기
class StoreError(Exception): ...
```

## 08단원 이후 — `todo/storage_sqlite.py`

```python
class SqliteTaskStore:                 # TaskList와 같은 메서드 (add/get/complete/remove/all/open_tasks/__len__)
    def __init__(self, conn: sqlite3.Connection)   # 테스트는 sqlite3.connect(":memory:")
    def init_schema(self) -> None
```

- 09: `add(title, tags=())`, `by_tag(tag) -> list[Task]`, 테이블 `tags`, `task_tags`
- 10: 인덱스 추가, `scripts/bench.py`
- 11: `move_tag(task_id, from_tag, to_tag)` 트랜잭션, `version` 열(낙관적 잠금)
- 12: `todo/migrations/001_init.sql`, `002_add_due.sql`, `migrate(conn)`; `due` 열
- 13: `todo/storage_document.py` (JSON 문서), `todo/cache_kv.py` (TTL dict), 재귀 CTE로 의존 관계
- 14: `todo/audit.py`, FTS5 가상 테이블 `tasks_fts`, `search(text)`

## 15단원 이후 — 계층

```python
# todo/repository.py
class TaskRepository(Protocol): add / get / complete / remove / all / open_tasks / by_tag / search
class MemoryTaskRepository, JsonTaskRepository, SqliteTaskRepository

# todo/service.py
class TaskService:
    def __init__(self, repo: TaskRepository, clock: Callable[[], datetime] = datetime.now)
    # 규칙은 여기: 빈 제목, 중복 완료, 마감일 과거 금지 등
```

## 17단원 이후 — HTTP API (`todo/api.py`, FastAPI)

| 메서드 | 경로 | 응답 |
| --- | --- | --- |
| GET | /tasks?done=false&limit=20&cursor= | 200, `{"items": [...], "next_cursor": ...}` |
| POST | /tasks | 201 Task / 422 |
| GET | /tasks/{id} | 200 / 404 |
| POST | /tasks/{id}/complete | 200 / 404 / 409(이미 완료) |
| DELETE | /tasks/{id} | 204 / 404 |
| GET | /health | 200 `{"status": "ok"}` |

오류 응답은 항상 `{"error": {"code": "...", "message": "..."}}`.

- 18: `POST /auth/register`, `POST /auth/login`, `Authorization: Bearer`, 할 일은 소유자만
- 19: `ETag`/`If-None-Match`, 서비스 계층 캐시와 무효화
- 20: `todo/worker.py`, 완료 시 알림을 큐에 넣고 워커가 발송
- 21: `web/index.html`, `web/app.js` — API를 호출하는 화면
- 22: `notifier/` 별도 서비스(FastAPI), HTTP로 호출
- 26: `Idempotency-Key` 헤더 지원 (`todo/idempotency.py`)
- 27: `todo/ratelimit.py` 토큰 버킷, 429 + `Retry-After`
- 28: `todo/circuit.py`, 알림 실패 시 폴백
- 31: 구조화 로그, 요청 id 미들웨어
- 32: `GET /metrics`
- 34: `.github/workflows/ci.yml`
- 35: `Dockerfile`, 환경 변수 설정 `todo/config.py`
- 37: `docker-compose.yml` (앱 2개 + nginx)
- 43: `todo/mcp_server.py` — 할 일 API를 MCP 도구로 노출
- 45: `POST /tasks/parse` — 자연어 → Task 초안 (LLM)
- 46: `GET /tasks/ask?q=` — RAG

## 테스트 규약

- 파일 이름 `test_unitNN.py` (저장소 전체에서 유일). 실행은 **단원별로**: `pytest units/NN-slug`
- 외부 네트워크·실제 LLM 호출은 테스트에서 금지. 가짜(fake)로 대체.
- 시간·난수는 주입한다 (`clock`, `rng` 인자).
