"""27단원: 속도 제한(rate limiting) — 토큰 버킷(token bucket).

버킷 하나에 토큰이 최대 capacity 개 들어가고, 초당 rate 개씩 다시 채워집니다.
요청 하나가 토큰 cost 개를 꺼내 갑니다. 토큰이 모자라면 거절하고 "언제 다시 오면 되는지"(retry_after)를 알려 줍니다.
키(key)마다 버킷을 따로 두면 "사용자별 제한"이 됩니다.

핵심은 "토큰을 주기적으로 채우는 백그라운드 작업"이 아니라, **요청이 올 때 지난 시간만큼 한 번에 채우는** 지연 계산(lazy refill)입니다.
그래서 시계(clock)만 주입하면 1초도 기다리지 않고 테스트할 수 있습니다.

TODO 를 채워 `pytest units/27-rate-limiting` 를 통과시키세요.
"""

from __future__ import annotations

import math
import time
from typing import Callable


class RateLimiter:
    """키별 토큰 버킷.

    rate:     초당 채워지는 토큰 수 (예: 5.0 → 1초에 5개, 0.2초에 1개)
    capacity: 버킷의 최대 토큰 수 = 순간적으로 허용하는 최대 연속 요청 수(burst)
    clock:    초 단위 단조 시계. 기본은 time.monotonic (벽시계가 뒤로 가도 영향 없음)

    rate <= 0 또는 capacity < 1 이면 ValueError.
    """

    def __init__(self, rate: float, capacity: int, clock: Callable[[], float] = time.monotonic) -> None:
        # TODO: 인자 검증 후 저장. 키별 상태는 dict[str, tuple[float, float]] (토큰 수, 마지막 갱신 시각) 정도면 충분하다.
        raise NotImplementedError

    def tokens(self, key: str) -> float:
        """지금 이 키의 버킷에 든 토큰 수(리필을 반영한 값). 처음 보는 키는 capacity.

        리필 규칙: tokens = min(capacity, tokens + (now - last) * rate)
        """
        # TODO
        raise NotImplementedError

    def allow(self, key: str, cost: int = 1) -> tuple[bool, float]:
        """요청을 허용할지 결정한다. (허용 여부, retry_after 초) 를 돌려준다.

        - cost < 1 또는 cost > capacity 면 ValueError (capacity 보다 큰 요청은 영원히 허용될 수 없다)
        - 토큰이 cost 이상이면: cost 만큼 빼고 (True, 0.0)
        - 모자라면: 토큰을 빼지 않고 (False, 부족분 / rate)
          부족분 = cost - 현재 토큰. 예: rate=2, 토큰 0, cost 1 → 0.5초 뒤에 다시 오라
        """
        # TODO
        raise NotImplementedError


def retry_after_header(seconds: float) -> str:
    """HTTP Retry-After 헤더 값. 정수 초 문자열이며 올림한다. 최소 "1".

    0.3 → "1", 2.0 → "2", 2.1 → "3"
    """
    # TODO
    raise NotImplementedError
