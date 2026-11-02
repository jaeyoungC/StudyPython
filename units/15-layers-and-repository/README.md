# 15 — 계층 분리와 리포지토리 패턴

## 목표

14단원까지 `TaskList`, `JsonTaskStore`, `SqliteTaskStore` 세 저장 방식이 제각각 자랐습니다. 이 단원이 끝나면
**규칙(서비스)과 저장(리포지토리)을 분리**해, 같은 테스트를 세 저장소에서 모두 통과시키고,
"현재 시각" 같은 바깥세상을 주입해 테스트가 시간을 멈출 수 있게 만듭니다. 16~17단원의 HTTP 화면은
이 서비스 위에 얹힙니다.

## 노트와의 연결

노트는 초급 아키텍트가 답해야 할 질문으로 "**시스템 분해와 상태의 위치**"를 꼽고,
"**상태는 어디에 두고, 인증은 어디서 처리하는가?**"라고 묻습니다. 이 단원은 그 질문의 가장 작은 형태입니다.
상태(할 일 목록)는 리포지토리 뒤에 두고, 규칙은 서비스에 두고, 화면은 아직 CLI 하나뿐이지만 다음 단원에 HTTP가
하나 더 생깁니다. 화면이 둘이 되어도 규칙이 한 곳에만 있으려면 지금 나눠 두어야 합니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| 계층(layer)과 리포지토리(repository) | 화면 → 서비스 → 리포지토리 → 저장소. 위 계층은 아래 계층의 인터페이스만 알고, 아래는 위를 모른다. 리포지토리는 "컬렉션처럼 보이는 저장소" | [Martin Fowler, Repository](https://martinfowler.com/eaaCatalog/repository.html) |
| `typing.Protocol` | 상속 없이 "이 메서드들이 있으면 된다"로 타입을 정하는 구조적 타이핑(structural typing). 세 리포지토리는 `TaskRepository` 를 상속하지 않는다 | [typing — Protocol](https://docs.python.org/ko/3/library/typing.html#typing.Protocol) |
| 의존성 주입(dependency injection)과 테스트 대역(test double) | 서비스가 리포지토리와 시계를 **직접 만들지 않고 생성자에서 받는다**. 그래서 테스트는 가짜(fake) 리포지토리와 멈춘 시계를 꽂을 수 있다 | [Martin Fowler, Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) |

테스트 대역의 종류는 섞어 쓰기 쉬우니 처음부터 구분합니다.

- **가짜(fake)**: 진짜처럼 동작하지만 가볍다. `MemoryTaskRepository` 가 그렇다.
- **스텁(stub)**: 정해진 값만 돌려준다. `fixed_clock` 이 그렇다(항상 같은 시각).
- **모의 객체(mock)**: 어떻게 호출됐는지를 검사한다. 테스트 파일의 `RecordingFakeRepository` 는 fake 에 호출 기록을 붙인 것이고,
  24단원에서 제대로 다룹니다.

pytest 새 기능 하나: `@pytest.fixture(params=[...])`. 픽스처에 params 를 주면 그 픽스처를 쓰는 테스트가 param 수만큼 반복됩니다.
`parametrize` 가 **입력**을 바꾼다면, params 픽스처는 **환경**을 바꿉니다.

## 과제

`todo/repository.py` 와 `todo/service.py` 의 `TODO` 를 채워 `pytest units/15-layers-and-repository` 를 통과시키세요.
14단원까지의 완성본(`models.py`, `storage_json.py`, `storage_sqlite.py`, `audit.py`, `migrations/`)은 그대로 두고 **감싸기만** 합니다.

| 파일 | 만드는 것 | 통과할 테스트 |
| --- | --- | --- |
| `todo/repository.py` | `MemoryTaskRepository` (TaskList 감싸기), `JsonTaskRepository` (호출마다 load → 바꾸기 → save), `SqliteTaskRepository` (SqliteTaskStore 위임) | `test_repo_*` × 3 저장소 |
| `todo/service.py` | `TaskService.add` (빈 제목·과거 마감일 금지), `complete` (중복 완료 → `AlreadyDoneError`), `list(done=None/True/False)`, `by_tag`, `search`, `overdue` (주입된 시계 기준) | `test_service_*` × 3 저장소 |

메서드 이름과 시그니처는 `docs/project-api.md` 의 "15단원 이후" 절과 같습니다. 바꾸지 마세요. 17단원의 API가 이 이름을 그대로 씁니다.

권장 순서: `MemoryTaskRepository` → 서비스 → 나머지 두 리포지토리. 메모리 구현으로 서비스 테스트가 먼저 초록이 되면,
남은 빨간 테스트는 "저장소 차이" 때문이라는 것을 바로 알 수 있습니다.

## 스스로 답해 볼 질문

1. `TaskList.complete` 와 `SqliteTaskStore.complete` 에도 "이미 완료면 ValueError" 가 있는데 서비스가 또 검사합니다. 규칙이 두 군데 있으면 무엇이 위험한가요? 어디가 "진짜" 규칙이어야 하나요?
2. `MemoryTaskRepository.search` 는 부분 문자열, `SqliteTaskRepository.search` 는 FTS5 단어 단위입니다. "SQL 공부"를 "공"으로 검색하면 둘의 결과가 다릅니다. 테스트가 이 차이를 피해 가고 있는데, 이것은 정직한 테스트인가요? 계약을 어떻게 적어야 할까요?
3. `JsonTaskRepository` 는 호출마다 파일 전체를 읽고 씁니다. 할 일 1만 개일 때 `add` 한 번의 비용은? 이것을 고치는 두 가지 방법(캐시, 파일 분할)의 대가는? → 19단원
4. `clock` 을 주입하지 않고 서비스 안에서 `datetime.now()` 를 부르면 `test_service_rejects_due_in_the_past` 를 어떻게 써야 할까요? 그 테스트는 2027년에도 통과할까요?
5. 서비스가 리포지토리의 `all()` 을 받아 파이썬에서 거르는 것(`list(done=True)`)과 리포지토리에 `done_tasks()` 를 추가하는 것, 어느 쪽이 나은가요? 할 일이 100개일 때와 100만 개일 때 답이 같은가요?

## 함정

- `Protocol` 을 **상속**하면 구조적 타이핑의 의미가 사라집니다. `class MemoryTaskRepository(TaskRepository)` 가 아니라 그냥 `class MemoryTaskRepository` 입니다.
- `JsonTaskRepository` 에서 `_load()` 를 두 번 부르면 서로 다른 `TaskList` 두 개가 생깁니다. 한 메서드 안에서는 한 번만 읽고, 그 객체를 바꾸고, 그 객체를 저장하세요.
- 서비스에서 `date.today()` 나 `datetime.now()` 를 직접 부르면 테스트가 날짜에 따라 깨집니다. 반드시 `self.today()` 를 쓰세요.
- `repo.all()` 이 내부 리스트를 그대로 돌려주면 `test_repo_returns_new_lists` 가 실패합니다. 03단원의 교훈이 계층을 넘어도 유효합니다.
- 픽스처가 `yield` 를 쓰면 `yield` 뒤는 테스트가 끝난 뒤 실행됩니다(정리). `sqlite` 연결은 그렇게 닫습니다.

## 완료 기준

- [ ] `pytest units/15-layers-and-repository` 18개 테스트 함수(세 저장소로 반복되어 50개 항목) 전부 통과
- [ ] 테스트 **1개 직접 추가**: 리포지토리 계약 중 아직 안 적힌 것(예: 태그가 없는 할 일에 `by_tag` 는?)
- [ ] `docs/adr/0008-layers-and-repository.md`: 왜 계층을 나눴고, 규칙을 서비스에만 두기로 했는지. "다시 볼 신호"에 질문 1의 답을 적기
- [ ] `NOTES.md`: 배운 것 3가지 / 헷갈린 것 1가지 / 다음 단원에 바꿀 것, 그리고 **세 문장 설명**("리포지토리가 뭔지"를 비개발자에게)
- [ ] **AI 코드 리뷰**: 서비스 코드를 리뷰받고 지적 하나 반영, 하나 반박
- [ ] **에이전트에게 작은 과제**(이번 단원부터): `cli.py` 가 `JsonTaskStore` 대신 `TaskService` + `JsonTaskRepository` 를 쓰도록 바꾸는 일을 에이전트에게 맡기세요. 맡기기 전에 스펙(바뀌면 안 되는 것: 명령·종료 코드·출력 형식)을 적고, 맡긴 뒤 `pytest` 와 `python -m todo ls` 로 직접 검증하고, 에이전트가 건드린 파일 목록을 NOTES.md 에 남기세요
- [ ] 브랜치 `unit-15` → PR → 스스로 리뷰 → 머지

## 더 깊이

- `python -m pytest units/15-layers-and-repository --durations=5` 로 가장 느린 테스트를 보세요. JSON 리포지토리가 왜 느린가요?
- `TaskRepository` 에 `add_many(titles)` 를 추가한다면 세 구현 중 어느 것이 트랜잭션으로 보호되고 어느 것이 중간에 실패하면 반쯤 저장될까요? 11단원의 ACID가 계층 위로 어떻게 새어 나오는지 생각해 보세요.
- Martin Fowler의 [PresentationDomainDataLayering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html): 계층을 나누는 것이 항상 옳지는 않습니다. 언제 과한가요?
