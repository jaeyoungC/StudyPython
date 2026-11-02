"""28단원: 점진적 기능 저하 — 서킷 브레이커(circuit breaker), 폴백(fallback), 격벽(bulkhead).

25단원의 재시도는 "잠깐 실패"를 견딥니다. 그런데 notifier 가 10분째 죽어 있다면? 요청마다 3번 재시도 × 2초 타임아웃이면
할 일 완료 한 번에 6초가 걸리고, 그 6초 동안 스레드 하나가 묶입니다. 서킷 브레이커는 "지금은 부르지도 말자"를 자동으로 결정합니다.

이 파일은 뼈대만 있습니다. 상태 기계는 README 의 그림을 보고 직접 설계하세요. 테스트(test_unit28.py)도 뼈대만 있으므로
먼저 테스트의 본문을 채운 뒤 구현합니다.
"""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Iterator, TypeVar

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"  # 정상. 호출을 통과시키고 실패를 센다
    OPEN = "open"  # 차단. 호출하지 않고 즉시 CircuitOpenError
    HALF_OPEN = "half_open"  # 시험. 호출 하나를 통과시켜 본다


class CircuitOpenError(Exception):
    """서킷이 열려 있어 호출하지 않았다. 호출하는 쪽은 폴백을 쓰거나 사용자에게 '나중에' 를 보여 준다."""


class CircuitBreaker:
    """실패가 failure_threshold 번 연속되면 OPEN, recovery_timeout 초 뒤 HALF_OPEN, 시험 호출이 성공하면 CLOSED.

    - clock 은 time.monotonic 과 같은 의미의 단조 시계 (주입용)
    - 어떤 예외를 '실패'로 셀지는 failure_on 으로 정한다 (ValueError 같은 호출자 잘못은 세지 않는다)
    - HALF_OPEN 에서 시험 호출이 실패하면 즉시 다시 OPEN, 성공하면 CLOSED 로 가고 실패 횟수를 0으로
    - 상태 전이는 '호출 시점'에 지연 평가한다 (타이머 스레드 없음) — 27단원의 지연 리필과 같은 생각
    """

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        failure_on: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError),
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        # TODO: 인자 검증, 상태·연속 실패 횟수·열린 시각 저장. 여러 스레드가 부른다면 threading.Lock 도 고려
        raise NotImplementedError

    @property
    def state(self) -> CircuitState:
        """현재 상태. OPEN 인데 recovery_timeout 이 지났다면 HALF_OPEN 을 돌려준다."""
        # TODO
        raise NotImplementedError

    def call(self, fn: Callable[[], T]) -> T:
        """상태에 따라 fn() 을 호출하거나 CircuitOpenError 를 던진다. 결과(성공/실패)를 기록한다."""
        # TODO
        raise NotImplementedError

    def record_success(self) -> None:
        # TODO
        raise NotImplementedError

    def record_failure(self) -> None:
        # TODO
        raise NotImplementedError


def with_fallback(fn: Callable[[], T], fallback: Callable[[BaseException], T], *, on: tuple[type[BaseException], ...] = (Exception,)) -> T:
    """fn() 이 on 에 속하는 예외를 던지면 fallback(예외) 의 결과를 돌려준다.

    폴백은 '덜 좋은 답'이어야지 '거짓 답'이면 안 된다. 예: 알림 실패 → "나중에 다시 보냄" 큐에 적재 (O),
    추천 목록 실패 → 빈 목록 (O), 결제 실패 → 성공한 척 (X)
    """
    # TODO
    raise NotImplementedError


class BulkheadFullError(Exception):
    """격벽이 꽉 찼다. 대기하지 않고 즉시 거절한다."""


class Bulkhead:
    """동시에 max_concurrent 개까지만 어떤 자원(예: notifier 호출)을 쓰게 하는 격벽.

    배의 격벽처럼, 한 구역(느린 외부 호출)이 물에 잠겨도 다른 구역(할 일 CRUD)은 뜬다.
    힌트: threading.Semaphore(max_concurrent) 와 acquire(blocking=False)
    """

    def __init__(self, max_concurrent: int) -> None:
        # TODO
        raise NotImplementedError

    @contextmanager
    def slot(self) -> Iterator[None]:
        """with bulkhead.slot(): ... 자리가 없으면 BulkheadFullError. 블록을 나가면 자리를 돌려준다(예외가 나도)."""
        # TODO
        raise NotImplementedError
        yield  # pragma: no cover  (contextmanager 가 제너레이터임을 유지하기 위한 줄)

    @property
    def available(self) -> int:
        """지금 비어 있는 자리 수."""
        # TODO
        raise NotImplementedError
