# 27 — 속도 제한

## 목표

클라이언트(사용자·에이전트)별로 **초당 요청 수를 제한하는 토큰 버킷**을 만들고, 초과 요청에는 `429 Too Many Requests` 와
`Retry-After` 헤더로 "언제 다시 오라"를 알려 줍니다. 시계를 주입해 기다림 없이 테스트합니다.

## 노트와의 연결

노트는 에이전트가 호출하는 시스템의 인프라 수요로 "사람보다 훨씬 많은 호출 → 속도 제한, 캐시, 사용량에 따른 비용 구조"를 꼽고,
신뢰성 영역에서 "API 속도 제한 같은 장애 대응"을 말합니다. 사람 한 명은 1분에 몇 번 클릭하지만 루프에 빠진 에이전트는 1초에 수백 번
호출합니다. 속도 제한은 그 한 클라이언트가 **다른 모든 사용자의 서비스를 끌어내리지 못하게** 하는 울타리이고, 동시에 "얼마나 쓰면 얼마를
내는가"라는 비용 구조의 기초 단위입니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| 토큰 버킷(token bucket) | 용량 `capacity` 의 양동이에 초당 `rate` 개씩 토큰이 찬다. 요청은 토큰을 꺼내 쓴다. 평소엔 `rate` 로 제한하면서 짧은 폭주(burst)는 `capacity` 만큼 허용한다. 요청이 올 때 지난 시간만큼 한꺼번에 채우는 **지연 리필(lazy refill)** 이면 타이머가 필요 없다 | [SRE Book: Handling Overload](https://sre.google/sre-book/handling-overload/) |
| 429 와 `Retry-After` | 상태 코드 429 는 "너무 많이 보냈다", `Retry-After: 3` 은 "3초 뒤에 오라". 잘 만든 클라이언트(25단원의 재시도)는 이 값을 읽어 백오프 대신 쓴다 | [RFC 6585 (429)](https://datatracker.ietf.org/doc/html/rfc6585), [RFC 9110 Retry-After](https://datatracker.ietf.org/doc/html/rfc9110#name-retry-after) |
| 제한의 키(key)와 단조 시계 | 무엇을 기준으로 세는가: 사용자 id, API 키, IP. 시간은 `time.monotonic()` — 벽시계(`time.time()`)는 NTP 보정으로 뒤로 갈 수 있다 | [time.monotonic](https://docs.python.org/ko/3/library/time.html#time.monotonic) |

다른 알고리즘도 있습니다. 고정 윈도(fixed window)는 "분당 60개"를 세지만 59초와 61초에 60개씩 보내면 2초 만에 120개가 통과합니다.
슬라이딩 윈도(sliding window)는 그것을 고치지만 요청 기록을 들고 있어야 합니다. 토큰 버킷은 키당 숫자 두 개(토큰, 마지막 시각)면 충분해 가장 널리 쓰입니다.

## 과제

`ratelimit.py` 의 `TODO` 를 채워 `pytest units/27-rate-limiting` 를 통과시키세요.

| 할 일 | 하는 일 |
| --- | --- |
| `RateLimiter(rate, capacity, clock)` | 인자 검증. 키별 `(토큰, 마지막 갱신 시각)` 보관 |
| `tokens(key)` | 리필을 반영한 현재 토큰 수. 처음 보는 키는 `capacity` |
| `allow(key, cost=1) -> (bool, retry_after)` | 충분하면 빼고 `(True, 0.0)`, 모자라면 빼지 않고 `(False, 부족분 / rate)` |
| `retry_after_header(seconds)` | 올림한 정수 초 문자열, 최소 `"1"` |

### 프로젝트에 붙이기

| 어디에 | 무엇을 |
| --- | --- |
| `todo/ratelimit.py` | 이 모듈을 옮긴다 |
| `todo/api.py` — 미들웨어(middleware) | 모든 `/tasks*` 요청 앞에서 `limiter.allow(key)`. 키는 18단원 인증의 `user_id`, 로그인 전 경로(`/auth/*`)는 클라이언트 IP. 거절이면 `429` + `Retry-After: retry_after_header(...)` + 오류 본문 `{"error": {"code": "rate_limited", "message": "..."}}` |
| 값 정하기 | 사람용 기본값 예: `rate=5, capacity=20`. 에이전트용 API 키는 별도 등급(`rate=50, capacity=200`)을 두고 ADR 에 근거를 적는다 |
| `/health` | 제한에서 **제외**한다. 35단원의 헬스 체크가 429 를 받으면 멀쩡한 서버가 죽은 것으로 보인다 |
| 응답 헤더(선택) | `X-RateLimit-Limit`, `X-RateLimit-Remaining` 을 붙이면 클라이언트가 거절 전에 속도를 줄일 수 있다 |
| 여러 인스턴스(37단원 예고) | 메모리 dict 는 프로세스마다 따로다. 인스턴스가 둘이면 실제 한도는 두 배가 된다. 공유 저장소(Redis 등)로 옮기는 것은 37단원에서 다룬다 |

`docs/adr/0019-rate-limiting.md` 에 "키 기준, 등급별 수치, 제외 경로, 메모리 저장소의 한계"를 남기세요.

## 스스로 답해 볼 질문

1. `rate=1, capacity=60` 과 `rate=60, capacity=1` 은 둘 다 "분당 60개"처럼 보입니다. 사용자 경험은 어떻게 다른가요?
2. 거절된 요청이 토큰을 깎으면 무슨 일이 생기나요? 폭주하는 에이전트는 영원히 429 만 받게 될까요? 그것은 좋은 일인가요?
3. 키를 IP 로 하면 같은 회사 사무실(같은 공인 IP) 사용자 50명은 어떻게 되나요? 키를 사용자 id 로 하면 로그인 전 요청은 어떻게 세나요?
4. `Retry-After` 를 0.3초 대신 "1"로 올림해서 돌려주는 이유는 무엇일까요? 그 1초 동안 토큰은 몇 개 찼나요?
5. 속도 제한을 API 서버 안에 둘 때와 그 앞단(nginx, API 게이트웨이)에 둘 때의 트레이드오프(지연·일관성·비용)는?

## 함정

- `time.time()` 을 쓰면 시계가 뒤로 갈 때 `now - last` 가 음수가 되어 토큰이 **줄어듭니다**. `time.monotonic()` 을 쓰세요.
- 리필 뒤 `min(capacity, ...)` 를 빼먹으면 한 시간 쉰 사용자가 수천 개를 한꺼번에 보낼 수 있습니다.
- 처음 보는 키를 토큰 0으로 시작하면 첫 요청부터 429 입니다. 가득 찬 상태로 시작해야 합니다.
- 키별 dict 는 키가 늘수록 자랍니다. 오래 안 쓴 키를 지우는 정리(eviction)가 없으면 메모리 누수입니다(더 깊이 참고).
- 429 응답을 25단원의 `retry` 가 즉시 재시도하면 상황이 나빠집니다. 클라이언트는 `Retry-After` 를 읽어 **그만큼** 기다려야 합니다.

## 완료 기준

- [ ] `pytest units/27-rate-limiting` 24개 테스트 전부 통과
- [ ] `todo/api.py` 에 속도 제한 미들웨어 적용. `TestClient` 로 "capacity+1 번째 요청이 429 이고 `Retry-After` 헤더가 있다", "`/health` 는 제한되지 않는다" 테스트 2개 추가(시계 주입)
- [ ] 고장 실험: 루프로 `POST /tasks` 를 200번 보내는 스크립트를 돌리고, 제한 전후의 응답 코드 분포와 p95 지연(10단원 `perf_counter`)을 `NOTES.md` 에 기록
- [ ] `docs/adr/0019-rate-limiting.md`
- [ ] `NOTES.md` 배운 것 3가지 / 헷갈린 것 1가지 / 다음 단원에 바꿀 것
- [ ] 세 문장 설명: "왜 어떤 요청은 '잠시 뒤 다시 시도하세요'를 받는가"
- [ ] AI 코드 리뷰: `allow` 를 리뷰받고, 스레드 안전성 지적이 나오면 `threading.Lock` 이 필요한 이유(11단원의 lost update)를 근거로 반영
- [ ] 에이전트에게 작은 과제: "`RateLimiter` 에 `forget_idle(older_than: float) -> int` 를 추가해 마지막 갱신이 `older_than` 초보다 오래된 키를 지우고 테스트 2개를 써라". 검토 포인트: 지운 키가 다시 오면 가득 찬 버킷으로 시작하는지
- [ ] 브랜치 `unit-27` → PR → 스스로 리뷰 → 머지

## 더 깊이

- 부하 차단(load shedding): 속도 제한이 "클라이언트별 공정성"이라면, 부하 차단은 "서버 전체가 살아남기"입니다. 둘의 차이를 [SRE Book: Handling Overload](https://sre.google/sre-book/handling-overload/) 에서 찾아보세요.
- 비용 구조: 토큰 버킷의 `cost` 인자를 "무거운 요청은 토큰 5개"처럼 쓰면 사용량 기반 과금의 기초가 됩니다. 43단원에서 에이전트용 API 를 설계할 때 다시 씁니다.
- 분산 토큰 버킷: 여러 인스턴스가 하나의 버킷을 공유하려면 Redis 의 원자적 연산(Lua 스크립트)을 씁니다. 37단원 뒤에 시도해 보세요.
