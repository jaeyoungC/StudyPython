"""17단원 테스트. 실행: pytest units/17-rest-api-fastapi

TestClient 는 서버를 띄우지 않고 앱을 직접 호출합니다(16단원처럼 스레드·포트가 필요 없다).
사용법은 requests/httpx 와 같습니다: client.get(path), client.post(path, json=...).
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from todo.api import create_app, decode_cursor, encode_cursor
from todo.repository import MemoryTaskRepository
from todo.service import TaskService


@pytest.fixture
def client():
    service = TaskService(MemoryTaskRepository(), clock=lambda: datetime(2026, 3, 1, 9, 0))
    return TestClient(create_app(service))


def make_tasks(client, n: int) -> None:
    for i in range(1, n + 1):
        assert client.post("/tasks", json={"title": f"할 일 {i}"}).status_code == 201


# --- 기본 경로 ---------------------------------------------------------------


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task_returns_201_and_body(client):
    response = client.post("/tasks", json={"title": "  SQL 공부 ", "tags": ["study"], "due": "2026-03-10"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "SQL 공부", "done": False, "tags": ["study"], "due": "2026-03-10"}


@pytest.mark.parametrize(
    "payload",
    [
        {},  # title 없음
        {"title": ""},  # 너무 짧음 (Pydantic)
        {"title": "   "},  # 공백만 (서비스 규칙)
        {"title": "x", "due": "어제"},  # 날짜 형식 아님
        {"title": "x", "due": "2026-02-28"},  # 과거 마감일 (서비스 규칙, 가짜 시계 기준)
        {"title": 123},  # 형식 틀림
    ],
)
def test_create_task_invalid_returns_422_with_envelope(client, payload):
    response = client.post("/tasks", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
    assert client.get("/tasks").json()["items"] == []  # 실패한 요청은 아무것도 만들지 않는다


def test_get_task_and_404_envelope(client):
    make_tasks(client, 1)
    assert client.get("/tasks/1").json()["title"] == "할 일 1"
    response = client.get("/tasks/99")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": response.json()["error"]["message"]}}


def test_get_task_with_non_integer_id_is_422(client):
    response = client.get("/tasks/abc")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_complete_200_then_409(client):
    make_tasks(client, 1)
    assert client.post("/tasks/1/complete").json()["done"] is True
    response = client.post("/tasks/1/complete")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "already_done"


def test_complete_missing_404(client):
    assert client.post("/tasks/5/complete").status_code == 404


def test_delete_204_without_body_then_404(client):
    make_tasks(client, 1)
    response = client.delete("/tasks/1")
    assert response.status_code == 204
    assert response.content == b""
    assert client.delete("/tasks/1").status_code == 404


# --- 목록과 페이지네이션 -------------------------------------------------------


def test_list_filters_by_done(client):
    make_tasks(client, 3)
    client.post("/tasks/2/complete")
    ids = lambda r: [t["id"] for t in r.json()["items"]]  # noqa: E731
    assert ids(client.get("/tasks")) == [1, 2, 3]
    assert ids(client.get("/tasks?done=false")) == [1, 3]
    assert ids(client.get("/tasks?done=true")) == [2]


def test_list_last_page_has_no_cursor(client):
    make_tasks(client, 2)
    body = client.get("/tasks?limit=5").json()
    assert [t["id"] for t in body["items"]] == [1, 2]
    assert body["next_cursor"] is None


def test_list_walks_pages_with_cursor(client):
    make_tasks(client, 5)
    seen = []
    cursor = None
    pages = 0
    while True:
        url = "/tasks?limit=2" + (f"&cursor={cursor}" if cursor else "")
        body = client.get(url).json()
        seen += [t["id"] for t in body["items"]]
        pages += 1
        cursor = body["next_cursor"]
        if cursor is None:
            break
    assert seen == [1, 2, 3, 4, 5]
    assert pages == 3


def test_cursor_survives_deletion_in_between(client):
    """offset 방식이라면 1페이지를 본 뒤 2번을 지우면 3번을 건너뛴다. 커서 방식은 건너뛰지 않는다."""
    make_tasks(client, 4)
    first = client.get("/tasks?limit=2").json()
    client.delete("/tasks/2")
    second = client.get(f"/tasks?limit=2&cursor={first['next_cursor']}").json()
    assert [t["id"] for t in second["items"]] == [3, 4]


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "limit=abc", "cursor=%%%", "cursor=bm90aGluZw=="])
def test_list_rejects_bad_limit_or_cursor(client, query):
    response = client.get(f"/tasks?{query}")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_cursor_round_trip():
    assert decode_cursor(encode_cursor(42)) == 42
    with pytest.raises(ValueError):
        decode_cursor("not-a-cursor")


# --- OpenAPI ------------------------------------------------------------------


def test_openapi_lists_every_route(client):
    spec = client.get("/openapi.json").json()
    assert {"/health", "/tasks", "/tasks/{task_id}", "/tasks/{task_id}/complete"} <= set(spec["paths"])
    assert "delete" in spec["paths"]["/tasks/{task_id}"]
    # 오류 응답 모양도 문서에 드러나야 호출자(사람·에이전트)가 미리 대비할 수 있다
    assert "ErrorBody" in spec["components"]["schemas"]
