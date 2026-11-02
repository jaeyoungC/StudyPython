"""16단원 테스트. 실행: pytest units/16-http-basics

서버를 별도 스레드에서 port=0(빈 포트 자동 선택)으로 띄우고, 표준 라이브러리 urllib 로 진짜 HTTP 요청을 보냅니다.
네트워크는 127.0.0.1 안에서만 오갑니다. 외부 인터넷에는 나가지 않습니다.
"""

import json
import threading
import urllib.error
import urllib.request
from datetime import datetime

import pytest

from todo.repository import MemoryTaskRepository
from todo.service import TaskService
from todo.simple_http import serve


@pytest.fixture
def base_url():
    service = TaskService(MemoryTaskRepository(), clock=lambda: datetime(2026, 3, 1))
    server = serve(service, port=0)  # 0 → OS 가 빈 포트를 고른다
    # poll_interval: shutdown() 이 루프가 멈추기를 기다리는 간격. 기본 0.5초면 테스트마다 0.5초씩 느려진다.
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.02), daemon=True)
    thread.start()
    host, port = server.server_address
    yield f"http://{host}:{port}"
    server.shutdown()  # serve_forever 루프 종료
    server.server_close()


def call(base_url: str, method: str, path: str, body: dict | None = None):
    """(status, headers, parsed_json_or_None) 을 돌려주는 작은 클라이언트.

    urllib 은 4xx/5xx 를 예외로 던지므로 받아서 같은 모양으로 돌려준다.
    """
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(base_url + path, data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        response = urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as error:
        response = error  # HTTPError 도 응답처럼 읽을 수 있다
    raw = response.read()
    parsed = json.loads(raw) if raw else None
    return response.status, response.headers, parsed


def test_health_returns_200_json(base_url):
    status, headers, body = call(base_url, "GET", "/health")
    assert status == 200
    assert headers["Content-Type"].startswith("application/json")
    assert body == {"status": "ok"}


def test_unknown_path_returns_404_with_error_envelope(base_url):
    status, _, body = call(base_url, "GET", "/nothing/here")
    assert status == 404
    assert body["error"]["code"] == "not_found"
    assert "message" in body["error"]


def test_post_task_returns_201_and_task(base_url):
    status, _, body = call(base_url, "POST", "/tasks", {"title": "SQL 공부", "tags": ["study"]})
    assert status == 201
    assert body["id"] == 1
    assert body["title"] == "SQL 공부"
    assert body["tags"] == ["study"]
    assert body["done"] is False


def test_post_empty_title_returns_422(base_url):
    status, _, body = call(base_url, "POST", "/tasks", {"title": "   "})
    assert status == 422
    assert body["error"]["code"] == "validation_error"


def test_post_invalid_json_returns_400(base_url):
    request = urllib.request.Request(base_url + "/tasks", data=b"{not json", method="POST")
    with pytest.raises(urllib.error.HTTPError) as info:
        urllib.request.urlopen(request, timeout=5)
    assert info.value.code == 400
    assert json.loads(info.value.read())["error"]["code"] == "bad_request"


def test_get_list_and_done_filter(base_url):
    call(base_url, "POST", "/tasks", {"title": "a"})
    call(base_url, "POST", "/tasks", {"title": "b"})
    call(base_url, "POST", "/tasks/1/complete")
    _, _, everything = call(base_url, "GET", "/tasks")
    _, _, open_only = call(base_url, "GET", "/tasks?done=false")
    _, _, done_only = call(base_url, "GET", "/tasks?done=true")
    assert [t["id"] for t in everything] == [1, 2]
    assert [t["id"] for t in open_only] == [2]
    assert [t["id"] for t in done_only] == [1]


def test_get_list_rejects_bad_done_value(base_url):
    status, _, body = call(base_url, "GET", "/tasks?done=maybe")
    assert status == 400
    assert body["error"]["code"] == "bad_request"


def test_get_one_task_and_404(base_url):
    call(base_url, "POST", "/tasks", {"title": "a"})
    status, _, body = call(base_url, "GET", "/tasks/1")
    assert (status, body["title"]) == (200, "a")
    status, _, body = call(base_url, "GET", "/tasks/99")
    assert (status, body["error"]["code"]) == (404, "not_found")


def test_complete_returns_200_then_409(base_url):
    call(base_url, "POST", "/tasks", {"title": "a"})
    status, _, body = call(base_url, "POST", "/tasks/1/complete")
    assert (status, body["done"]) == (200, True)
    status, _, body = call(base_url, "POST", "/tasks/1/complete")
    assert (status, body["error"]["code"]) == (409, "already_done")


def test_complete_missing_returns_404(base_url):
    status, _, _ = call(base_url, "POST", "/tasks/7/complete")
    assert status == 404


def test_delete_returns_204_without_body_then_404(base_url):
    call(base_url, "POST", "/tasks", {"title": "a"})
    status, headers, body = call(base_url, "DELETE", "/tasks/1")
    assert status == 204
    assert body is None
    assert headers["Content-Length"] == "0"
    status, _, _ = call(base_url, "DELETE", "/tasks/1")
    assert status == 404


def test_korean_title_survives_the_round_trip(base_url):
    """UTF-8 로 보내고 UTF-8 로 받는다. ensure_ascii=False 와 charset 헤더가 하는 일."""
    call(base_url, "POST", "/tasks", {"title": "한글 제목 ✓"})
    _, _, body = call(base_url, "GET", "/tasks/1")
    assert body["title"] == "한글 제목 ✓"
