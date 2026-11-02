"""FastAPI 로 만든 할 일 HTTP API (17단원).

create_app(service, users) 는 앱 팩토리(app factory)입니다. 서비스를 밖에서 받아서 앱을 만들기 때문에
테스트는 메모리 리포지토리를, 운영은 SQLite 리포지토리를 꽂을 수 있습니다 (15단원의 의존성 주입이 한 층 더 올라온 것).

21단원: cors_origins 를 주면 그 출처(origin)의 브라우저 화면이 이 API 를 부를 수 있다 (CORS 미들웨어).
20단원: /health 는 async def. 나머지 경로는 동기 서비스(sqlite 등)를 부르므로 def 로 두어 FastAPI 가 스레드풀에서 돌리게 한다.
19단원: GET /tasks 와 GET /tasks/{id} 는 ETag 를 붙이고, If-None-Match 가 같으면 본문 없이 304 를 돌려준다.
18단원: /auth/register, /auth/login 이 생기고, /tasks 아래는 모두 `Authorization: Bearer <토큰>` 이 있어야 한다.
현재 사용자는 Depends(current_user) 로 각 경로 함수에 주입된다.

실행: uvicorn todo.api:app --reload   →  http://127.0.0.1:8000/docs 에서 OpenAPI 문서
"""

from __future__ import annotations

import base64
import binascii
import hashlib
from collections.abc import Sequence

from fastapi import Depends, FastAPI, Header, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth import AuthError, User, UserStore
from .models import Task, TaskNotFoundError
from .repository import MemoryTaskRepository
from .schemas import Credentials, ErrorBody, TaskIn, TaskOut, TaskPage, TokenOut, UserOut
from .service import AlreadyDoneError, TaskService

MAX_LIMIT = 100


# --- 커서 페이지네이션 -------------------------------------------------------


def encode_cursor(last_id: int) -> str:
    """마지막으로 보낸 id 를 불투명한(opaque) 문자열로. 클라이언트는 내용을 해석하지 말고 그대로 돌려줘야 한다."""
    return base64.urlsafe_b64encode(f"id:{last_id}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    """encode_cursor 의 역. 손상된 커서는 ValueError."""
    try:
        text = base64.urlsafe_b64decode(cursor.encode()).decode()
        prefix, _, number = text.partition(":")
        if prefix != "id" or not number.isdigit():
            raise ValueError
        return int(number)
    except (binascii.Error, UnicodeDecodeError, ValueError) as error:
        raise ValueError("cursor 가 올바르지 않습니다") from error


def paginate(tasks: list[Task], limit: int, cursor: str | None) -> TaskPage:
    """id 오름차순으로 정렬된 tasks 에서 cursor 다음부터 limit 개를 잘라 낸다.

    offset 방식과 달리 중간에 항목이 지워져도 건너뛰거나 중복되지 않는다.
    """
    after = decode_cursor(cursor) if cursor else 0
    remaining = [t for t in tasks if t.id > after]
    page = remaining[:limit]
    next_cursor = encode_cursor(page[-1].id) if len(remaining) > limit else None
    return TaskPage(items=[TaskOut.from_task(t) for t in page], next_cursor=next_cursor)


# --- HTTP 캐시: ETag / If-None-Match -------------------------------------------


def make_etag(body: bytes) -> str:
    """본문의 해시. 본문이 같으면 ETag 도 같다. 따옴표까지가 ETag 문법이다."""
    return '"' + hashlib.sha256(body).hexdigest()[:32] + '"'


def json_with_etag(request: Request, model: BaseModel) -> Response:
    """모델을 JSON 으로 직렬화해 ETag 를 붙인다. 클라이언트의 If-None-Match 와 같으면 304(본문 없음).

    Cache-Control: no-cache 는 "저장하지 말라"가 아니라 "쓰기 전에 매번 서버에 물어보라(재검증)"는 뜻이다.
    """
    body = model.model_dump_json().encode("utf-8")
    etag = make_etag(body)
    headers = {"ETag": etag, "Cache-Control": "no-cache"}
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)
    return Response(content=body, media_type="application/json", headers=headers)


# --- 오류 응답 ------------------------------------------------------------------


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    body = ErrorBody.model_validate({"error": {"code": code, "message": message}})
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_error_handlers(app: FastAPI) -> None:
    """예외 → 상태 코드 번역을 한 곳에 모은다. 16단원의 _dispatch 와 같은 역할."""

    @app.exception_handler(TaskNotFoundError)
    async def not_found(_: Request, exc: TaskNotFoundError) -> JSONResponse:
        return error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))

    @app.exception_handler(AuthError)
    async def unauthorized(_: Request, exc: AuthError) -> JSONResponse:
        response = error_response(status.HTTP_401_UNAUTHORIZED, "unauthorized", str(exc))
        response.headers["WWW-Authenticate"] = "Bearer"  # 401 에는 "어떻게 인증하면 되는지"를 알려 주는 것이 규약
        return response

    @app.exception_handler(AlreadyDoneError)
    async def already_done(_: Request, exc: AlreadyDoneError) -> JSONResponse:
        return error_response(status.HTTP_409_CONFLICT, "already_done", str(exc))

    @app.exception_handler(ValueError)
    async def invalid_value(_: Request, exc: ValueError) -> JSONResponse:
        return error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, "validation_error", str(exc))

    @app.exception_handler(RequestValidationError)
    async def request_invalid(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0]
        where = ".".join(str(p) for p in first.get("loc", ()))
        return error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, "validation_error", f"{where}: {first.get('msg')}")


# --- 앱 팩토리 ------------------------------------------------------------------


def bearer_token(authorization: str | None = Header(default=None)) -> str:
    """'Authorization: Bearer xxx' 헤더에서 토큰만 꺼낸다. 없거나 형식이 다르면 AuthError."""
    if not authorization:
        raise AuthError("Authorization 헤더가 없습니다")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError("Authorization 헤더는 'Bearer <토큰>' 형식이어야 합니다")
    return token


def create_app(
    service: TaskService, users: UserStore | None = None, cors_origins: Sequence[str] = ()
) -> FastAPI:
    app = FastAPI(title="할 일 API", version="0.21.0")
    register_error_handlers(app)
    # TODO: cors_origins 가 비어 있지 않으면 CORSMiddleware 를 단다.
    #   app.add_middleware(CORSMiddleware, allow_origins=list(cors_origins), allow_methods=[...], allow_headers=[...], expose_headers=["ETag"])
    #   - allow_methods: 이 API 가 쓰는 GET, POST, DELETE 와 사전 요청용 OPTIONS
    #   - allow_headers: 화면이 보내는 Authorization, Content-Type, If-None-Match
    #   - "*" 출처는 Authorization 헤더와 함께 쓸 수 없다(브라우저 규칙). 출처를 적어라.
    users = users if users is not None else UserStore(clock=service.clock)
    responses = {401: {"model": ErrorBody}, 404: {"model": ErrorBody}, 409: {"model": ErrorBody}, 422: {"model": ErrorBody}}

    def current_user(token: str = Depends(bearer_token)) -> User:
        """의존성(dependency): 경로 함수가 `user: User = Depends(current_user)` 라고 적으면 FastAPI 가 먼저 이것을 부른다."""
        return users.user_for_token(token)

    @app.get("/health")
    async def health() -> dict:
        """async 경로 함수: 이벤트 루프에서 직접 돈다. 안에서 블로킹 호출(time.sleep, sqlite)을 하면 서버 전체가 멈춘다."""
        return {"status": "ok"}

    # -- 인증 ----------------------------------------------------------------

    @app.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, responses=responses)
    def register(body: Credentials) -> UserOut:
        try:
            user = users.register(body.username, body.password)
        except ValueError as error:
            if "이미 있는" in str(error):
                return error_response(status.HTTP_409_CONFLICT, "username_taken", str(error))  # type: ignore[return-value]
            raise
        return UserOut(id=user.id, username=user.username)

    @app.post("/auth/login", response_model=TokenOut, responses=responses)
    def login(body: Credentials) -> TokenOut:
        return TokenOut(access_token=users.login(body.username, body.password))

    # -- 할 일: 모두 로그인 필요, 자기 것만 ----------------------------------------

    @app.get("/tasks", response_model=TaskPage, responses=responses)
    def list_tasks(
        request: Request,
        user: User = Depends(current_user),
        done: bool | None = None,
        limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
        cursor: str | None = None,
    ) -> Response:
        page = paginate(service.list(done=done, owner_id=user.id), limit=limit, cursor=cursor)
        return json_with_etag(request, page)

    @app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED, responses=responses)
    def create_task(body: TaskIn, user: User = Depends(current_user)) -> TaskOut:
        return TaskOut.from_task(service.add(body.title, tags=body.tags, due=body.due, owner_id=user.id))

    @app.get("/tasks/{task_id}", response_model=TaskOut, responses=responses)
    def get_task(task_id: int, request: Request, user: User = Depends(current_user)) -> Response:
        return json_with_etag(request, TaskOut.from_task(service.get(task_id, owner_id=user.id)))

    @app.post("/tasks/{task_id}/complete", response_model=TaskOut, responses=responses)
    def complete_task(task_id: int, user: User = Depends(current_user)) -> TaskOut:
        return TaskOut.from_task(service.complete(task_id, owner_id=user.id))

    @app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, responses=responses)
    def delete_task(task_id: int, user: User = Depends(current_user)) -> Response:
        service.remove(task_id, owner_id=user.id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


# `uvicorn todo.api:app` 으로 바로 띄울 수 있도록 메모리 저장소로 기본 앱 하나를 만들어 둔다.
# 화면은 `python -m http.server 5500 -d web` 으로 띄우므로 그 출처를 허용한다.
app = create_app(TaskService(MemoryTaskRepository()), cors_origins=["http://127.0.0.1:5500", "http://localhost:5500"])
