"""asyncio 기초 (20단원): "기다리는 동안 다른 일을 한다"를 숫자로 확인하기.

- await asyncio.sleep(s) 는 "s 초 동안 기다리되, 그동안 다른 코루틴이 돌게 양보한다".
- time.sleep(s) 는 스레드 전체를 멈춘다. async 함수 안에서 불러도 아무도 못 돈다.
asyncio 가 이기는 조건은 하나: 기다림(I/O)이 많을 때. CPU 계산이 많을 때는 도움이 되지 않는다.
"""

from __future__ import annotations

import asyncio
import time


async def slow_step(name: str, seconds: float) -> str:
    """I/O 를 흉내 낸다: 기다리는 동안 이벤트 루프에 양보한다."""
    await asyncio.sleep(seconds)
    return name


async def run_sequential(names: list[str], seconds: float) -> list[str]:
    """하나 끝나면 다음. 총 시간 ≈ len(names) × seconds."""
    results = []
    for name in names:
        results.append(await slow_step(name, seconds))
    return results


async def run_concurrent(names: list[str], seconds: float) -> list[str]:
    """전부 동시에 시작. 총 시간 ≈ seconds. 결과 순서는 names 순서와 같다(gather 가 보장)."""
    return list(await asyncio.gather(*(slow_step(name, seconds) for name in names)))


async def blocking_step(name: str, seconds: float) -> str:
    """잘못된 예: async 안에서 time.sleep. 루프가 통째로 멈춰 gather 를 써도 빨라지지 않는다."""
    time.sleep(seconds)
    return name


async def run_concurrent_but_blocking(names: list[str], seconds: float) -> list[str]:
    return list(await asyncio.gather(*(blocking_step(name, seconds) for name in names)))


def timed(coro_factory, *args) -> tuple[list[str], float]:
    """코루틴을 실행하고 (결과, 걸린 초) 를 돌려준다. 테스트와 실험용."""
    start = time.perf_counter()
    result = asyncio.run(coro_factory(*args))
    return result, time.perf_counter() - start


if __name__ == "__main__":
    names = [f"작업{i}" for i in range(5)]
    for fn in (run_sequential, run_concurrent, run_concurrent_but_blocking):
        _, elapsed = timed(fn, names, 0.2)
        print(f"{fn.__name__:28s} {elapsed:.2f}초")
