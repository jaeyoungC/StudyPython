"""FastAPI 로 만든 할 일 HTTP API (17단원).

create_app(service) 는 앱 팩토리(app factory)입니다. 서비스를 밖에서 받아서 앱을 만들기 때문에
테스트는 메모리 리포지토리를, 운영은 SQLite 리포지토리를 꽂을 수 있습니다 (15단원의 의존성 주입이 한 층 더 올라온 것).

실행: uvicorn todo.api:app --reload   →  http://127.0.0.1:8000/docs 에서 OpenAPI 문서
"""

from __future__ import annotations

import base64
import binascii

from fastapi import FastAPI, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .models import Task, TaskNotFoundError
from .repository import MemoryTaskRepository
from .schemas import ErrorBody, TaskIn, TaskOut, TaskPage
from .service import AlreadyDoneError, TaskService

MAX_LIMIT = 100


# --- 커서 페이지네이션 -------------------------------------------------------


def encode_cursor(last_id: int) -> str:
    """마지막으로 보낸 id 를 불투명한(opaque) 문자열로. 클라이언트는 내용을 해석하지 말고 그대로 돌려줘야 한다.

    힌트: f"id:{last_id}" 를 base64.urlsafe_b64encode 로. 숫자를 그대로 노출하지 않는 이유는 README 의 질문 3.
    """
    # TODO
    raise NotImplementedError


def decode_cursor(cursor: str) -> int:
    """encode_cursor 의 역. 손상된 커서(base64 아님, 'id:' 접두사 없음, 숫자 아님)는 ValueError.

    힌트: base64 는 binascii.Error 를, 디코딩은 UnicodeDecodeError 를 던질 수 있다. 모두 ValueError 로 바꿔라(raise from).
    """
    # TODO
    raise NotImplementedError


def paginate(tasks: list[Task], limit: int, cursor: str | None) -> TaskPage:
    """id 오름차순으로 정렬된 tasks 에서 cursor 다음부터 limit 개를 잘라 낸다.

    - cursor 가 없으면 처음부터
    - 남은 항목이 limit 보다 많을 때만 next_cursor 를 준다 (마지막 페이지는 None)
    offset 방식과 달리 중간에 항목이 지워져도 건너뛰거나 중복되지 않는다.
    """
    # TODO
    raise NotImplementedError


# --- 오류 응답 ------------------------------------------------------------------


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    body = ErrorBody.model_validate({"error": {"code": code, "message": message}})
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_error_handlers(app: FastAPI) -> None:
    """예외 → 상태 코드 번역을 한 곳에 모은다. 16단원의 _dispatch 와 같은 역할."""

    @app.exception_handler(TaskNotFoundError)
    async def not_found(_: Request, exc: TaskNotFoundError) -> JSONResponse:
        return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))

    # TODO: AlreadyDoneError → 409 "already_done"
    # TODO: ValueError → 422 "validation_error"  (서비스 규칙 위반: 공백 제목, 과거 마감일, 잘못된 cursor)
    # TODO: RequestValidationError → 422 "validation_error"
    #       exc.errors()[0] 에 {"loc": (...), "msg": "..."} 가 있다. 메시지는 "body.title: String should have ..." 처럼.
    #       이 핸들러를 안 달면 FastAPI 기본 422 본문({"detail": [...]})이 나가 봉투 규칙이 깨진다.


# --- 앱 팩토리 ------------------------------------------------------------------


def create_app(service: TaskService) -> FastAPI:
    app = FastAPI(title="할 일 API", version="0.17.0")
    register_error_handlers(app)
    responses = {404: {"model": ErrorBody}, 409: {"model": ErrorBody}, 422: {"model": ErrorBody}}

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    # TODO: GET /tasks → TaskPage. 쿼리: done: bool | None, limit (1~MAX_LIMIT, 기본 20, Query(ge=, le=)), cursor
    #       service.list(done=done) 결과를 paginate 로.
    # TODO: POST /tasks → 201 TaskOut. 본문은 TaskIn. service.add(body.title, tags=body.tags, due=body.due)
    # TODO: GET /tasks/{task_id} → TaskOut
    # TODO: POST /tasks/{task_id}/complete → TaskOut
    # TODO: DELETE /tasks/{task_id} → 204, 본문 없음 (Response(status_code=204) 를 돌려준다)
    # 각 데코레이터에 responses=responses 를 주면 OpenAPI 문서에 오류 봉투가 실린다.

    return app


# `uvicorn todo.api:app` 으로 바로 띄울 수 있도록 메모리 저장소로 기본 앱 하나를 만들어 둔다.
app = create_app(TaskService(MemoryTaskRepository()))
