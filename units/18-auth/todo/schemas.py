"""HTTP 경계의 자료형 (Pydantic 모델).

도메인의 Task(dataclass)와 일부러 분리합니다. 바깥에 보여 주는 모양과 안에서 쓰는 모양은 따로 바뀝니다.
- TaskIn  : 클라이언트가 보내는 것. 검증 규칙(최소 길이 등)이 여기 붙는다. 어기면 FastAPI 가 422 를 만든다.
- TaskOut : 클라이언트에게 돌려주는 것. owner_id 는 내보내지 않는다(호출자는 이미 자기 것만 본다).
- TaskPage: 목록 응답. items 와 다음 페이지로 가는 next_cursor.
- ErrorBody: 모든 오류 응답의 모양 {"error": {"code", "message"}}.
- Credentials / TokenOut / UserOut: 18단원 인증.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from .models import Task


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="앞뒤 공백 제거 후 1자 이상")
    tags: list[str] = Field(default_factory=list)
    due: date | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool
    tags: list[str]
    due: date | None

    @classmethod
    def from_task(cls, task: Task) -> TaskOut:
        return cls(id=task.id, title=task.title, done=task.done, tags=list(task.tags), due=task.due)


class TaskPage(BaseModel):
    items: list[TaskOut]
    next_cursor: str | None = Field(default=None, description="다음 페이지 요청의 cursor 값. 없으면 마지막 페이지")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorBody(BaseModel):
    error: ErrorDetail


class Credentials(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=200)


class UserOut(BaseModel):
    id: int
    username: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
