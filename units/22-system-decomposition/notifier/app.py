"""알림 서비스의 FastAPI 앱.

경로:
    POST /notifications   본문 {"user_id": int | null, "message": str} → 202 {"id": n}
    GET  /notifications?user_id=   → 200 [{"id", "user_id", "message", "received_at"}, ...]
    GET  /health          → 200 {"status": "ok"}

이 서비스는 "알림을 받았다"는 사실만 안다. 할 일이 무엇인지, 사용자 이름이 무엇인지 모른다.
그것이 서비스를 나눈다는 것의 뜻이다: 각자 자기 데이터만 가진다.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from fastapi import FastAPI, status
from pydantic import BaseModel, Field


class NotificationIn(BaseModel):
    user_id: int | None = None
    message: str = Field(min_length=1, max_length=500)


class NotificationOut(BaseModel):
    id: int
    user_id: int | None
    message: str
    received_at: datetime


class NotificationStore:
    """메모리 저장. 이 서비스가 소유하는 유일한 데이터."""

    def __init__(self, clock: Callable[[], datetime] = datetime.now) -> None:
        self.clock = clock
        self._items: list[NotificationOut] = []

    def add(self, item: NotificationIn) -> NotificationOut:
        saved = NotificationOut(id=len(self._items) + 1, user_id=item.user_id, message=item.message, received_at=self.clock())
        self._items.append(saved)
        return saved

    def list(self, user_id: int | None = None) -> list[NotificationOut]:
        return [n for n in self._items if user_id is None or n.user_id == user_id]


def create_notifier_app(store: NotificationStore | None = None) -> FastAPI:
    store = store if store is not None else NotificationStore()
    app = FastAPI(title="알림 서비스", version="0.22.0")

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    # TODO: POST /notifications → 202 Accepted, 본문 {"id": n}. "받았다"이지 "전달했다"가 아니므로 201 이 아니라 202.
    # TODO: GET /notifications?user_id= → NotificationOut 리스트 (response_model=list[NotificationOut])

    return app


app = create_notifier_app()
