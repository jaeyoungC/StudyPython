"""25단원: 타임아웃·재시도·백오프.

외부 호출은 실패합니다. 문제는 "실패하느냐"가 아니라 "실패했을 때 얼마나 기다리고, 몇 번 다시 하고,
무엇은 다시 하지 않느냐"입니다. 이 모듈은 그 세 가지를 함수로 분리합니다.

- backoff_delay:     n번째 재시도 전에 얼마나 기다릴지 (지수 백오프 + 완전 지터)
- retry:             함수를 재시도하는 틀. 시간(sleep)과 난수(rng)는 주입받는다
- call_with_timeout: 함수에 시간 제한을 건다 (concurrent.futures)

TODO 를 채워 `pytest units/25-timeouts-and-retries` 를 통과시키세요.
"""

from __future__ import annotations

import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

T = TypeVar("T")

# 기본으로 재시도할 "일시적(transient)" 오류. ValueError 같은 "내 잘못"은 들어 있지 않다.
TRANSIENT_ERRORS: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError)


class RetryError(Exception):
    """모든 시도가 실패했을 때. 마지막 예외를 __cause__ 로 잇는다(raise ... from)."""

    def __init__(self, attempts: int, last_exception: BaseException) -> None:
        super().__init__(f"{attempts}번 시도 후 포기: {last_exception!r}")
        self.attempts = attempts
        self.last_exception = last_exception


def backoff_delay(attempt: int, *, base_delay: float, max_delay: float, rng: random.Random) -> float:
    """attempt(0부터)번째 재시도 전에 기다릴 시간(초).

    완전 지터(full jitter) 방식:
        cap = min(max_delay, base_delay * 2 ** attempt)
        return rng.uniform(0, cap)
    attempt < 0 이면 ValueError.
    """
    # TODO
    raise NotImplementedError


def retry(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    retry_on: tuple[type[BaseException], ...] = TRANSIENT_ERRORS,
    sleep: Callable[[float], Any] = time.sleep,
    rng: random.Random | None = None,
) -> T:
    """fn() 을 최대 attempts 번 시도한다.

    - attempts < 1 이면 ValueError
    - fn() 이 성공하면 그 값을 바로 돌려준다
    - retry_on 에 속하는 예외면 sleep(backoff_delay(i, ...)) 뒤 다시 시도한다. i 는 0, 1, 2, ...
      (즉 sleep 은 "시도 사이"에만 불린다. 마지막 실패 뒤에는 자지 않는다)
    - retry_on 에 속하지 않는 예외는 즉시 그대로 전파한다 (재시도·sleep 없음)
    - 마지막 시도까지 실패하면 RetryError 를 마지막 예외로부터(from) 던진다
    - rng 가 None 이면 random.Random() 을 쓴다
    """
    # TODO
    raise NotImplementedError


def call_with_timeout(
    fn: Callable[[], T],
    *,
    seconds: float,
    executor: ThreadPoolExecutor | None = None,
) -> T:
    """fn() 을 다른 스레드에서 실행하고 seconds 안에 끝나지 않으면 TimeoutError 를 던진다.

    - executor 가 None 이면 ThreadPoolExecutor(max_workers=1) 을 만들어 쓴다.
      이때 `with` 로 감싸지 마세요. with 는 블록을 나갈 때 작업이 끝날 때까지 기다리므로(shutdown(wait=True))
      타임아웃의 의미가 사라집니다. executor.shutdown(wait=False) 를 쓰세요.
    - future.result(timeout=seconds) 가 concurrent.futures.TimeoutError 를 던지면
      내장 TimeoutError(f"{seconds}초 안에 끝나지 않음") 로 바꿔 던진다.
      (Python 3.11부터 둘은 같은 클래스이지만, 메시지를 붙이기 위해 다시 던진다)
    - fn 이 던진 예외는 그대로 전파한다
    - 한계: 타임아웃이 나도 스레드 안의 fn 은 계속 돈다. README의 "함정" 참고.
    """
    # TODO
    raise NotImplementedError
