# 2주차 — 클래스 · dataclass · 타입 힌트 · 예외

## 목표

1주차의 딕셔너리를 `Task` 클래스로 바꾸고, 규칙(검증)과 상태를 한 곳에 모읍니다.
노트의 "상태는 어디에 두는가?" 질문을 코드 수준에서 처음 마주하는 주입니다.

## 공부할 개념 (2~3시간)

- `@dataclass`, `field(default_factory=...)`, `__post_init__` 에서 검증하기
- 타입 힌트: `int`, `str`, `list[Task]`, `Task | None`
- 직접 만든 예외 클래스: `class TaskNotFoundError(Exception)`
- 캡슐화: 리스트를 밖에 그대로 노출하지 않고 메서드로만 바꾸게 하기

참고: [dataclasses 문서](https://docs.python.org/ko/3/library/dataclasses.html),
[사용자 정의 예외](https://docs.python.org/ko/3/tutorial/errors.html#user-defined-exceptions)

## 과제 (3~5시간)

`task_model.py` 의 `TODO` 를 채워 `pytest weeks/week02` 를 통과시키세요.

- `Task`: `id`, `title`, `done=False`. 만들어질 때 제목 공백을 정리하고, 빈 제목이면 `ValueError`
- `Task.complete()`: 완료 처리. 이미 완료된 할 일이면 `ValueError` (규칙을 객체 안에 둔다)
- `TaskList`: 할 일 목록을 감싸는 클래스. `add`, `get`, `complete`, `remove`, `open_tasks`, `__len__`
- 없는 id면 `TaskNotFoundError` (`ValueError` 대신 의미가 분명한 예외)

## 스스로 답해 볼 질문

1. 1주차에는 "빈 제목 금지" 규칙이 `add_task` 함수에 있었습니다. 지금은 `Task` 안에 있습니다. 어느 쪽이 더 안전할까요?
2. `TaskList.open_tasks()` 가 내부 리스트를 그대로 돌려주면 어떤 일이 생길 수 있을까요?
3. `TaskNotFoundError` 를 `ValueError` 의 하위 클래스로 만들면 무엇이 편해질까요?

## 완료 기준

- [ ] `pytest weeks/week02` 전부 통과
- [ ] 1주차 CLI를 `TaskList` 를 쓰도록 바꿔 보기 (선택)
- [ ] `NOTES.md` 작성
