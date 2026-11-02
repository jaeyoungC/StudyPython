"""알림 발송기 (20단원). 실제 발송(이메일, 푸시)은 느리고 실패할 수 있는 바깥세상이다.

Notifier 는 Protocol 이라 어떤 구현이든 꽂힌다.
- FakeNotifier    테스트용 가짜(fake): 보낸 것을 기억만 한다.
- ConsoleNotifier 개발용: 터미널에 찍는다.
- 22단원: HttpNotifier — 별도 서비스에 HTTP 로 보낸다.
"""

from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    def send(self, user_id: int | None, message: str) -> None: ...


class FakeNotifier:
    def __init__(self, fail_times: int = 0) -> None:
        self.sent: list[tuple[int | None, str]] = []
        self.fail_times = fail_times  # 처음 n 번은 일부러 실패한다 (워커의 오류 처리 테스트용)
        self.failures = 0

    def send(self, user_id: int | None, message: str) -> None:
        if self.failures < self.fail_times:
            self.failures += 1
            raise ConnectionError("알림 서버에 연결할 수 없습니다 (가짜)")
        self.sent.append((user_id, message))


class ConsoleNotifier:
    def send(self, user_id: int | None, message: str) -> None:
        print(f"[알림 → 사용자 {user_id}] {message}")
