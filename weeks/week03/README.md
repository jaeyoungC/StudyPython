# 3주차 — 파일 입출력 · JSON · 첫 ADR

## 목표

프로그램을 꺼도 할 일이 남도록 JSON 파일에 저장합니다. 노트의 "데이터 영속화"와,
"파일이 깨지면 어떻게 되는가?"라는 신뢰성 질문을 처음 다룹니다.

## 공부할 개념 (2~3시간)

- `pathlib.Path`, `open(..., encoding="utf-8")`, `json.dumps / json.loads`
- `ensure_ascii=False` 가 한글 저장에 왜 필요한가
- 원자적 쓰기(atomic write): 임시 파일에 다 쓴 뒤 `os.replace` 로 바꿔치기 → 쓰다가 꺼져도 원본이 깨지지 않음
- 예외 감싸기: `json.JSONDecodeError` 를 내 프로그램의 `StoreError` 로 바꿔 올리기 (`raise ... from error`)

참고: [json 문서](https://docs.python.org/ko/3/library/json.html), [os.replace](https://docs.python.org/ko/3/library/os.html#os.replace)

## 과제 (3~5시간)

`json_store.py` 의 `TODO` 를 채워 `pytest weeks/week03` 을 통과시키세요.

| 함수 | 하는 일 |
| --- | --- |
| `save_tasks(path, tasks)` | 할 일 리스트(딕셔너리)를 JSON으로 저장. 한글이 그대로 보이게, 원자적으로 |
| `load_tasks(path)` | 파일이 없으면 `[]`. 내용이 깨졌거나 리스트가 아니면 `StoreError` |

테스트는 pytest의 `tmp_path` (테스트마다 새 임시 폴더)를 씁니다. 실제 파일을 건드리지 않는 방법입니다.

## ADR 쓰기 (1시간)

`docs/adr/0000-template.md` 를 복사해 `docs/adr/0001-store-tasks-in-json.md` 를 쓰세요.
대안으로 "CSV 파일", "SQLite"를 놓고 비교해 보세요. 4~6주차에 이 결정을 다시 보게 됩니다.

## 스스로 답해 볼 질문

1. 할 일이 10만 개라면 할 일 하나를 완료할 때마다 파일 전체를 다시 쓰는 방식은 괜찮을까요?
2. 프로그램 두 개가 같은 파일에 동시에 저장하면 어떻게 될까요? → 6주차
3. 파일이 깨졌을 때 `[]` 를 돌려주는 대신 오류를 내는 이유는 무엇일까요? (힌트: 다음 저장 때 무슨 일이?)

## 완료 기준

- [ ] `pytest weeks/week03` 전부 통과
- [ ] ADR-0001 작성
- [ ] `NOTES.md` 작성
