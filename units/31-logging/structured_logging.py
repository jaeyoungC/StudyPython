"""31단원: 로깅 — 구조화(JSON) 로그, 요청 id, 개인정보 가리기.

print 는 "지금 내 눈"을 위한 것이고, 로그는 "새벽 3시에 장애를 조사하는 미래의 나(또는 검색 도구)"를 위한 것입니다.
그래서 로그는 (1) 기계가 읽을 수 있는 형식(JSON 한 줄), (2) 한 요청의 로그를 모두 묶어 주는 열쇠(요청 id),
(3) 남기면 안 되는 것(비밀번호·토큰·이메일)의 제거가 필요합니다.

구성:
- request_id_var / request_context: contextvars 로 "지금 처리 중인 요청의 id"를 들고 다닌다
- redact:                           dict/list 안의 민감한 키의 값을 "[REDACTED]" 로 바꾼다
- JsonFormatter:                    logging.Formatter 를 상속해 레코드를 JSON 한 줄로 만든다
- configure_logging:                루트 로거에 JsonFormatter 핸들러를 (한 번만) 단다

TODO 를 채워 `pytest units/31-logging` 를 통과시키세요.
"""

from __future__ import annotations

import json
import logging
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Iterator, TextIO

# "지금 이 실행 흐름이 처리 중인 요청의 id". 스레드·async 작업마다 따로 보인다.
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

REDACTED = "[REDACTED]"
SENSITIVE_KEYS: frozenset[str] = frozenset({"password", "token", "authorization", "api_key", "secret", "email"})

# LogRecord 가 기본으로 갖는 속성들. extra={...} 로 들어온 사용자 필드를 골라내는 데 쓴다.
_STANDARD_ATTRS: frozenset[str] = frozenset(
    {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module", "exc_info",
        "exc_text", "stack_info", "lineno", "funcName", "created", "msecs", "relativeCreated", "thread",
        "threadName", "processName", "process", "message", "asctime", "taskName",
    }
)


def new_request_id() -> str:
    """새 요청 id. uuid4 의 16진수 32자."""
    return uuid.uuid4().hex


@contextmanager
def request_context(request_id: str | None = None) -> Iterator[str]:
    """블록 안에서 request_id_var 를 설정하고, 나갈 때 이전 값으로 되돌린다.

    - request_id 가 None 이면 new_request_id() 로 만든다
    - yield 로 실제 사용된 id 를 내보낸다
    - 힌트: token = request_id_var.set(...) ... finally: request_id_var.reset(token)
    """
    # TODO
    raise NotImplementedError


def redact(value: Any, sensitive_keys: frozenset[str] = SENSITIVE_KEYS) -> Any:
    """dict 안에서 키 이름(대소문자 무시)이 sensitive_keys 에 들면 값을 REDACTED 로 바꾼 **새 객체**를 돌려준다.

    - dict 와 list 는 재귀적으로 내려간다
    - 그 밖의 값(str, int, None, ...)은 그대로
    - 입력을 바꾸지 않는다
    """
    # TODO
    raise NotImplementedError


class JsonFormatter(logging.Formatter):
    """LogRecord → JSON 한 줄.

    키 순서와 내용:
      ts         record.created 를 UTC ISO 8601 로. datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
      level      record.levelname
      logger     record.name
      message    record.getMessage()  (%s 인자가 채워진 문자열)
      request_id request_id_var.get()  (없으면 null)
      ...        extra={...} 로 들어온 필드들(_STANDARD_ATTRS 에 없는 record.__dict__ 의 키). redact 를 거친다
      exc_info   예외가 있으면 self.formatException(record.exc_info) 문자열. 없으면 키 자체를 넣지 않는다
    json.dumps(..., ensure_ascii=False, default=str)  — datetime 처럼 JSON 이 모르는 값은 str() 로
    """

    def __init__(self, *, sensitive_keys: frozenset[str] = SENSITIVE_KEYS) -> None:
        super().__init__()
        self.sensitive_keys = sensitive_keys

    def format(self, record: logging.LogRecord) -> str:
        # TODO
        raise NotImplementedError


def configure_logging(level: int = logging.INFO, stream: TextIO | None = None) -> logging.Logger:
    """루트 로거에 JsonFormatter 를 단 StreamHandler 를 설치하고 루트 로거를 돌려준다.

    - 여러 번 불러도 핸들러가 하나만 남아야 한다. 힌트: 자신이 만든 핸들러에 표시(handler._structured = True)를
      해 두고, 다음 호출에서 그 표시가 있는 핸들러만 제거한다. (다른 핸들러 — 예: pytest 의 caplog — 는 건드리지 않는다)
    - stream 이 None 이면 StreamHandler() 기본값(stderr)
    """
    # TODO
    raise NotImplementedError
