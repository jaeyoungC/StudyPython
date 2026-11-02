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


class HttpNotifier:
    """별도 알림 서비스(notifier/)에 HTTP 로 보낸다 (22단원).

    client 를 주입받는 이유: 테스트는 TestClient(notifier 앱)를 넣고, 운영은 httpx.Client(timeout=...) 를 넣는다.
    timeout 이 없는 바깥 호출은 없다. 알림 서비스가 멈추면 워커 스레드가 영원히 기다리게 되기 때문이다.
    """

    def __init__(self, base_url: str, client=None, timeout: float = 2.0) -> None:
        import httpx  # FastAPI 와 함께 설치되는 HTTP 클라이언트. 표준 라이브러리 urllib 보다 타임아웃·JSON 다루기가 편하다

        self.base_url = base_url.rstrip("/")
        self.client = client if client is not None else httpx.Client(timeout=timeout)
        self.timeout = timeout

    def send(self, user_id: int | None, message: str) -> None:
        """POST {base_url}/notifications {"user_id": ..., "message": ...}. 2xx 가 아니면 예외 (워커가 failed 로 센다).

        힌트: self.client.post(url, json=..., timeout=self.timeout) → response.raise_for_status()
        연결 실패는 httpx.HTTPError 로 올라온다. 잡지 말고 그대로 올려라. 판단은 워커의 몫이다.
        """
        # TODO
        raise NotImplementedError
