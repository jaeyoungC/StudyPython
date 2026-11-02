"""24단원: 테스트 전략 — 외부 의존성을 주입받는 함수와 테스트 대역(test double).

이 모듈은 "할 일을 완료하면 주인에게 알림을 보낸다"는 작은 기능입니다.
알림을 실제로 보내는 부분(Sender)은 바깥에서 주입받으므로, 테스트에서는
가짜(fake)·스텁(stub)·목(mock) 세 가지 대역으로 바꿔 끼울 수 있습니다.

TODO 를 채워 `pytest units/24-testing-strategy` 를 통과시키세요.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Protocol


class Sender(Protocol):
    """알림을 보내는 외부 의존성의 계약(contract).

    15단원의 Protocol과 같습니다. send 는 전달에 성공하면 True, 실패하면 False 를 돌려줍니다.
    예외를 던지지 않고 False 를 돌려주는 것이 이 계약의 약속입니다.
    """

    def send(self, to: str, message: str) -> bool: ...


@dataclass(frozen=True)
class NotifyResult:
    delivered: bool
    message: str


def summarize(tasks: list[dict]) -> dict:
    """할 일 목록의 통계를 돌려준다. 외부 의존성이 전혀 없는 순수 함수(pure function).

    반환 형식: {"total": int, "done": int, "open": int, "done_ratio": float}
    - done_ratio 는 done / total. total 이 0이면 0.0
    - 입력 리스트를 바꾸지 않는다
    """
    # TODO
    raise NotImplementedError


def build_message(task: dict, now: datetime) -> str:
    """알림 본문을 만든다.

    형식: "[YYYY-MM-DD HH:MM] 할 일 완료: <제목>"
    예:   "[2026-11-02 09:30] 할 일 완료: SQL 공부"
    힌트: now.strftime("%Y-%m-%d %H:%M")
    """
    # TODO
    raise NotImplementedError


def notify_completed(
    task: dict,
    owner_email: str,
    sender: Sender,
    clock: Callable[[], datetime] = datetime.now,
) -> NotifyResult:
    """완료된 할 일을 주인에게 알린다.

    - task["done"] 이 False 면 ValueError. 이때 sender.send 는 호출하면 안 된다.
    - owner_email 에 "@" 가 없으면 ValueError. 역시 send 를 호출하면 안 된다.
    - 본문은 build_message(task, clock()) 로 만든다.
    - sender.send(owner_email, 본문) 의 반환값을 NotifyResult.delivered 에 담는다.
    """
    # TODO
    raise NotImplementedError


class FileSender:
    """'진짜' 어댑터의 가장 단순한 형태: 파일 끝에 한 줄씩 기록한다.

    완성되어 있습니다. 수정하지 마세요. 테스트에서는 FakeSender 와 같은 계약 테스트를 통과하는지
    확인하는 데 씁니다(README의 "계약 테스트" 참고).
    한 줄 형식: "<받는 사람>\\t<본문>\\n"
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def send(self, to: str, message: str) -> bool:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{to}\t{message}\n")
        return True
