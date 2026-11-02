# 07 — 파일 · JSON · 원자적 쓰기

## 목표

프로그램을 꺼도 할 일이 남도록 `Task` 객체들을 JSON 파일에 저장하고 다시 읽습니다.
그리고 "저장하다가 꺼지면?", "파일이 깨져 있으면?"이라는 **신뢰성 질문**을 처음 코드로 다룹니다.
첫 번째 ADR을 씁니다.

> 폴더의 `todo/models.py`, `todo/cli.py`는 06단원까지의 완성본입니다. 이 단원의 `TODO`는 `todo/storage_json.py`와 `cli.py`의 `main` 안 세 줄뿐입니다.

## 노트와의 연결

노트는 "AI 시스템은 데이터 소스가 보여주는 것만 본다. 데이터 아키텍처를 잘못 고르면 AI는 자기가 무엇을 모르는지조차 모른다"고 하고,
데이터 결정을 "되돌리는 비용이 가장 큰 결정"이라고 부릅니다. 이 단원의 저장 형식 선택(JSON 파일)은 작은 결정이지만
08단원에서 SQLite로 바꿀 때 무엇이 아프고 무엇이 안 아픈지 직접 겪게 됩니다. 그래서 ADR을 오늘 씁니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| `pathlib`와 `json` | `Path.read_text / write_text(encoding="utf-8")`, `json.dumps(..., ensure_ascii=False, indent=2)`, `json.loads` | [pathlib](https://docs.python.org/ko/3/library/pathlib.html), [json](https://docs.python.org/ko/3/library/json.html) |
| 원자적 쓰기(atomic write) | 임시 파일에 다 쓴 뒤 `os.replace(tmp, path)`. 쓰는 도중 꺼져도 원본은 멀쩡하거나 새 파일이거나 둘 중 하나 | [os.replace](https://docs.python.org/ko/3/library/os.html#os.replace) |
| 예외 감싸기 | 라이브러리 예외(`json.JSONDecodeError`)를 내 프로그램의 예외(`StoreError`)로 바꿔 올리기. `raise StoreError(...) from error`로 원인을 보존 | [8.5 예외 연쇄](https://docs.python.org/ko/3/tutorial/errors.html#exception-chaining) |

### 왜 그냥 `write_text`로 덮어쓰면 안 되나

`path.write_text(...)`는 파일을 먼저 비우고 쓰기 시작합니다. 그 사이에 프로세스가 죽으면 **빈 파일 또는 반쯤 쓴 파일**이 남습니다.
할 일 100개가 한순간에 사라지는 길입니다. 임시 파일에 다 쓴 뒤 이름을 바꾸면, 이름 바꾸기는 운영체제가 한 번에 처리하므로
중간 상태가 없습니다.

## 과제

`todo/storage_json.py`와 `todo/cli.py`의 `TODO`를 채워 `pytest units/07-json-store`를 통과시키세요.

| 항목 | 하는 일 |
| --- | --- |
| `StoreError(Exception)` | 저장 파일을 읽을 수 없을 때 |
| `JsonTaskStore(path)` | 경로를 기억 |
| `.load() -> list[Task]` | 파일이 없으면 `[]`. JSON이 깨졌거나, 최상위가 리스트가 아니거나, 항목이 `Task.from_dict`를 통과하지 못하면 `StoreError` (원인 예외를 `from`으로 연결) |
| `.save(tasks)` | `Task.to_dict()` 목록을 JSON으로, 한글이 그대로 보이게, **원자적으로** 저장. 임시 파일은 같은 폴더에 `.tmp` 확장자 |
| `cli.main`의 `--file` | 명령 실행 전에 `load`로 `TaskList`를 채우고, 명령이 성공하면 `save` |

실행해 보기:

```bash
cd units/07-json-store
python -m todo add "산책"
python -m todo add "SQL 공부"
python -m todo ls                 # 이제 남아 있다
cat todo.json                     # 한글이 그대로 보여야 한다
```

### ADR-0001 쓰기

`docs/adr/0000-template.md`를 복사해 `docs/adr/0001-store-tasks-in-json-file.md`를 씁니다.
대안으로 **CSV 파일**과 **SQLite**를 놓고 비교하고, "이 결정을 다시 볼 신호"를 꼭 적으세요(예: 할 일이 1만 개를 넘으면, 두 프로그램이 동시에 쓰면).
08단원이 끝나면 이 ADR을 다시 읽게 됩니다.

## 스스로 답해 볼 질문

1. 할 일이 10만 개라면, 하나를 완료할 때마다 파일 전체를 다시 쓰는 방식은 괜찮을까요? 어디서부터 아파질까요?
2. 두 터미널에서 동시에 `python -m todo add`를 하면 어떻게 될까요? (11단원 동시성)
3. 파일이 깨졌을 때 `[]`를 돌려주는 대신 `StoreError`를 내는 이유는? 힌트: 그다음 `save`가 일어나면 무슨 일이?
4. `from error`를 빼고 `raise StoreError("깨짐")`만 하면 디버깅할 때 무엇을 잃나요?

## 함정

- `ensure_ascii=False`를 빼면 한글이 `산책`로 저장됩니다. 동작은 하지만 사람이 못 읽습니다.
- 임시 파일을 `/tmp` 같은 **다른 디스크**에 만들면 `os.replace`가 원자적이지 않을 수 있습니다. 같은 폴더에 만드세요.
- `save` 도중 예외가 나면 임시 파일이 남을 수 있습니다. `try/finally`로 지우거나, 최소한 `.gitignore`의 `*.tmp`가 왜 있는지 이해하세요.
- `load`에서 `Task.from_dict`가 던지는 `ValueError`도 `StoreError`로 감싸야 합니다. 테스트가 손으로 고친 잘못된 파일을 넣어 봅니다.

## 완료 기준

- [ ] `pytest units/07-json-store` 전부 통과
- [ ] `python -m todo`로 할 일을 넣고 프로그램을 다시 실행해도 남아 있음
- [ ] `docs/adr/0001-store-tasks-in-json-file.md` 작성 (대안 2개, 다시 볼 신호 1개 이상)
- [ ] `NOTES.md`: 질문 1~4의 내 답
- [ ] **세 문장 설명**: "왜 임시 파일에 쓰고 이름을 바꾸는가"를 비개발자에게 세 문장으로 (NOTES.md)
- [ ] 브랜치 `unit-07` → PR → 머지

## 더 깊이

- `os.fsync`를 찾아보세요. `os.replace`만으로 정전에도 안전할까요? 데이터베이스가 "내구성(durability)"을 위해 무엇을 하는지 11단원에서 이어집니다.
- JSON 대신 한 줄에 할 일 하나씩 쓰는 **JSON Lines**(`.jsonl`) 형식이면 "추가"는 어떻게 달라질까요? 전체를 다시 쓰지 않아도 될까요? 대신 "수정"은?
