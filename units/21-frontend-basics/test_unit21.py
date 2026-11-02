"""21단원 테스트 뼈대. 실행: pytest units/21-frontend-basics

브라우저를 띄우는 테스트는 없습니다(그건 24단원 E2E 에서). 여기서는 두 가지만 자동으로 확인합니다.
1. API 쪽 CORS 동작 (TestClient 로 Origin 헤더를 흉내)
2. HTML/JS 파일의 정적 검사 (라벨, 버튼 type, textContent 사용 등) — 완벽하진 않지만 되돌아가는 것을 막는다
나머지(키보드만으로 조작, 낭독기)는 README 의 손 점검 목록으로 합니다.
"""

import re
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from todo.api import create_app
from todo.repository import MemoryTaskRepository
from todo.service import TaskService

WEB = Path(__file__).parent / "web"
ORIGIN = "http://127.0.0.1:5500"


@pytest.fixture
def client():
    service = TaskService(MemoryTaskRepository(), clock=lambda: datetime(2026, 3, 1, 9, 0))
    return TestClient(create_app(service, cors_origins=[ORIGIN]))


@pytest.fixture
def html():
    return (WEB / "index.html").read_text(encoding="utf-8")


@pytest.fixture
def js():
    return (WEB / "app.js").read_text(encoding="utf-8")


# --- CORS ------------------------------------------------------------------------


def test_preflight_allows_registered_origin(client):
    """OPTIONS /tasks 에 Origin, Access-Control-Request-Method: POST, Access-Control-Request-Headers: authorization 을 보내면 200 이고
    access-control-allow-origin 이 ORIGIN, allow-methods 에 POST 와 DELETE, allow-headers 에 authorization 이 있다."""
    pytest.fail("아직 구현하지 않음")


def test_simple_request_gets_cors_headers_and_exposes_etag(client):
    """GET /health 에 Origin 을 붙이면 access-control-allow-origin 이 ORIGIN 이고 access-control-expose-headers 에 ETag 가 있다."""
    pytest.fail("아직 구현하지 않음")


def test_unknown_origin_gets_no_cors_headers(client):
    """Origin: http://evil.example 로 GET /health 를 보내면 200 이지만 access-control-allow-origin 헤더가 없다. (서버는 응답하고, 막는 것은 브라우저다)"""
    pytest.fail("아직 구현하지 않음")


def test_no_cors_when_origins_not_configured():
    """cors_origins 없이 만든 앱은 Origin 을 보내도 access-control-allow-origin 이 없다. 기본값은 닫힘."""
    pytest.fail("아직 구현하지 않음")


# --- HTML 정적 검사 ---------------------------------------------------------------


def test_html_declares_language_and_charset(html):
    """<html lang="ko"> 와 <meta charset="utf-8"> 가 있다. 낭독기의 발음과 한글 깨짐을 막는다."""
    pytest.fail("아직 구현하지 않음")


def test_every_input_has_a_label(html):
    """모든 <input id="X"> 와 <select id="X"> 에 대해 <label for="X"> 가 있다. (정규식으로 id 와 for 를 모아 집합 비교)"""
    pytest.fail("아직 구현하지 않음")


def test_every_button_has_explicit_type(html):
    """모든 <button> 에 type="submit" 또는 type="button" 이 있다. 기본값(submit)에 기대면 폼 안의 보조 버튼이 폼을 보내 버린다."""
    pytest.fail("아직 구현하지 않음")


def test_status_region_is_announced(html):
    """id="status" 요소에 role="status" 또는 aria-live 가 있다."""
    pytest.fail("아직 구현하지 않음")


def test_task_list_has_accessible_name(html):
    """<ul id="task-list"> 에 aria-label 이 있다."""
    pytest.fail("아직 구현하지 않음")


# --- JS 정적 검사 -----------------------------------------------------------------


def test_js_never_uses_innerhtml(js):
    """app.js 에 'innerHTML' 이 없다. 제목은 textContent 로만 넣는다 (XSS 방지)."""
    pytest.fail("아직 구현하지 않음")


def test_js_sends_bearer_token_and_handles_error_envelope(js):
    """'Authorization' 과 'Bearer' 문자열, 그리고 'body.error' (봉투 해석) 가 있다."""
    pytest.fail("아직 구현하지 않음")


def test_js_renders_from_state_only(js):
    """render 함수 본문 안에 'fetch(' 와 'api(' 호출이 없다. render 는 state 를 읽기만 한다. (함수 본문을 정규식이나 문자열 슬라이스로 잘라 검사)"""
    pytest.fail("아직 구현하지 않음")
