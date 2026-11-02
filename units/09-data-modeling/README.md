# 09 — 데이터 모델링과 정규화

## 목표

할 일에 **태그(tag)** 기능을 붙입니다. 한 할 일에 태그 여러 개, 한 태그에 할 일 여러 개 — 다대다(N:M) 관계입니다.
"어떤 조회를 자주 하는가"를 **먼저** 적고, 그에 맞춰 테이블 세 개(`tasks`, `tags`, `task_tags`)로 쪼개고,
`JOIN` 으로 다시 합치고, `GROUP BY` 로 셉니다. 이 단원이 끝나면 요구사항을 듣고 테이블 모양을 그릴 수 있습니다.

## 노트와의 연결

노트가 데이터 설계에서 묻는 두 질문이 이 단원의 뼈대입니다: "**가장 자주 일어나는 조회는 무엇인가? 이 스키마는 나중에
바꾸기 얼마나 어려운가?**" 또 노트는 "데이터는 에이전트가 마이그레이션을 도와도 한번 정하면 바꾸기 어렵다. 되돌리는
비용이 가장 큰 결정이다"라고 경고합니다. 태그를 `tasks` 에 쉼표로 이어 붙일지, 별도 테이블로 뺄지는 5분이면 정하지만,
데이터가 쌓인 뒤 바꾸려면 12단원의 마이그레이션이 필요합니다. 그래서 이 단원은 코드보다 **접근 패턴 목록**을 먼저 쓰게 합니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| 접근 패턴(access pattern) → 스키마 | 테이블을 그리기 전에 "누가, 무엇을, 얼마나 자주 읽고 쓰는가" 목록부터. 스키마는 그 목록에 대한 답 | [SQLite — 외래 키](https://sqlite.org/foreignkeys.html) (관계를 DB 가 지키게 하는 장치), 『데이터 중심 애플리케이션 설계』(Kleppmann) 2장 "데이터 모델과 질의 언어" |
| 1:N, N:M 과 연결 테이블(join table), 정규화(normalization) | 같은 사실을 한 곳에만 적는다. N:M 은 반드시 가운데 테이블이 필요하다. 복합 기본 키 `PRIMARY KEY (task_id, tag_id)` | [SQLite — CREATE TABLE 의 제약](https://sqlite.org/lang_createtable.html#constraints), [위키백과 — 데이터베이스 정규화](https://ko.wikipedia.org/wiki/데이터베이스_정규화) |
| `JOIN` 과 `GROUP BY` | 쪼갠 테이블을 조건으로 다시 합치기, 묶어서 세기(`COUNT`) | [SQLite — SELECT 의 JOIN](https://sqlite.org/lang_select.html#strange_join_names), [GROUP BY](https://sqlite.org/lang_select.html#generation_of_the_set_of_result_rows) |

### 접근 패턴부터 적기

태그 기능의 요구사항을 "조회·변경 목록"으로 바꾸면 이렇습니다. **스키마는 이 표의 답**입니다.

| # | 패턴 | 빈도(추정) | 스키마가 답하는 방법 |
| --- | --- | --- | --- |
| A | 할 일 하나를 보여 줄 때 태그도 같이 | 매우 잦음 (목록 화면마다) | `task_tags WHERE task_id = ?` + `tags` JOIN |
| B | 태그 하나로 할 일 거르기 (`ls --tag 공부`) | 잦음 | `tags WHERE name = ?` → `task_tags WHERE tag_id = ?` |
| C | 태그별 개수 (사이드바) | 가끔 | `GROUP BY tag_id` |
| D | 할 일 삭제 시 태그 연결도 삭제 | 가끔 | `ON DELETE CASCADE` |
| E | 태그 이름 바꾸기 ("공부"→"학습") | 드묾 | `tags` 한 행만 `UPDATE` — 정규화의 보상 |

패턴 E 가 결정적입니다. 태그를 `tasks.tags_csv = "공부,운동"` 처럼 문자열로 넣으면 A 는 쉽지만 B 는 `LIKE '%공부%'` 로
전체를 훑어야 하고("공부"가 "공부방"에도 걸립니다), E 는 모든 행을 고쳐 써야 합니다. 같은 사실("이 태그 이름은 공부다")을
여러 행에 복사해 두었기 때문입니다. **한 사실은 한 곳에** — 이것이 정규화의 핵심이고, 그 대가가 JOIN 입니다.

### 세 테이블의 모양

```
tasks                tags               task_tags (연결 테이블)
---------            ---------          -----------------------
id  PK               id   PK            task_id  FK → tasks.id ┐ 복합 PK
title                name UNIQUE        tag_id   FK → tags.id  ┘
done
```

`task_tags` 는 "할 일 3번에 태그 2번이 붙었다"는 사실만 적는 행의 모음입니다. 복합 기본 키가 같은 쌍의 중복을 막고,
외래 키(foreign key, FK)가 "존재하지 않는 할 일"에 태그를 붙이는 것을 막습니다. SQLite 는 FK 검사를 **기본으로 꺼 두므로**
연결마다 `PRAGMA foreign_keys = ON` 을 켜야 합니다 (`SqliteTaskStore.__init__` 에 이미 있습니다).

### JOIN 읽는 법

```sql
SELECT tasks.id, tasks.title, tasks.done
FROM tasks
JOIN task_tags ON task_tags.task_id = tasks.id   -- tasks 의 각 행에 연결 행을 붙이고
JOIN tags      ON tags.id = task_tags.tag_id     -- 그 연결 행에 태그 행을 붙인 뒤
WHERE tags.name = ?                              -- 태그 이름으로 거른다
ORDER BY tasks.id;
```

`JOIN … ON` 은 "두 테이블의 행을 이 조건이 참인 쌍끼리 붙여라"입니다. 연결 테이블을 거치면 JOIN 이 두 번 필요합니다.

```sql
SELECT tags.name, COUNT(task_tags.task_id)
FROM tags
JOIN task_tags ON task_tags.tag_id = tags.id
GROUP BY tags.id;        -- 같은 태그끼리 한 묶음으로 만들고, 묶음마다 COUNT
```

`GROUP BY` 가 있으면 `SELECT` 에는 묶음 기준 열과 집계 함수(`COUNT`, `SUM`, `MAX` …)만 올 수 있다고 생각하면 안전합니다.

## 과제

1. **코드를 짜기 전에** `NOTES.md` 에 접근 패턴 표를 **내 말로** 다시 쓰세요. 위 표에 없는 패턴이 하나라도 떠오르면 추가하세요
   (예: "태그가 하나도 없는 할 일만 보기"). 그 패턴에 세 테이블 구조가 잘 답하는지도 적으세요.
2. `todo/storage_sqlite.py` 의 `TODO` 를 채워 `pytest units/09-data-modeling` 를 모두 통과시키세요.

| 만들 것 | 하는 일 | 관련 테스트 |
| --- | --- | --- |
| `SCHEMA` 의 `tags`, `task_tags` | UNIQUE, 복합 PK, FK + CASCADE | `test_schema_*`, `test_tag_names_are_unique`, `test_link_to_missing_task_*`, `test_same_tag_cannot_*` |
| `_tags_of(task_id)` | 패턴 A: 한 할 일의 태그 이름들 (JOIN, ORDER BY name) | `test_add_with_tags_*`, `test_all_and_open_tasks_include_tags` |
| `_attach_tag`, `add(title, tags=())` | 태그 행 재사용(`INSERT OR IGNORE`), 연결 행 추가, 빈 제목이면 아무것도 남기지 않음 | `test_add_*`, `test_same_tag_name_is_stored_once` |
| `by_tag(tag)` | 패턴 B: 3-테이블 JOIN | `test_by_tag_*` |
| `tag_counts()` | 패턴 C: GROUP BY + COUNT | `test_tag_counts_*` |
| (이미 구현) `remove` | 패턴 D: CASCADE 가 연결 행을 지움 — FK 가 켜져 있어야 통과 | `test_remove_deletes_links_*` |

`todo/models.py` 에는 `Task.tags` 와 `normalize_tags` 가, `todo/cli.py` 에는 `add --tag`, `ls --tag` 가 이미 들어 있습니다.
CLI 는 아직 JSON 저장소를 씁니다 — JSON 에서는 태그를 그냥 리스트로 넣으면 끝인데 SQLite 에서는 테이블이 둘이나 더 필요한 이유를
생각해 보세요 (13단원에서 정면으로 비교합니다).

## 스스로 답해 볼 질문

1. 태그를 `tasks` 테이블에 `tags_csv TEXT` 열 하나로 넣는 설계와 비교해, 패턴 A~E 각각에서 어느 쪽이 유리한가요? 표로 적어 보세요.
   "모든 패턴에서 이기는 설계"가 있나요?
2. `tags.name` 에 UNIQUE 가 없으면 무슨 일이 생기나요? `INSERT OR IGNORE` 는 어떤 제약에 기대어 동작하나요?
3. `remove()` 뒤에도 `tags` 행은 남습니다(`test_remove_deletes_links_but_keeps_tag_row`). 남기는 게 맞을까요, 지우는 게 맞을까요?
   어떤 접근 패턴이 있으면 답이 바뀌나요?
4. `all()` 은 할 일 N 개에 대해 `_tags_of` 를 N 번 부릅니다(쿼리 N+1 개). 할 일이 1만 개면 어떻게 될까요?
   한 번의 쿼리로 끝내려면 SQL 을 어떻게 바꿔야 할까요? (`GROUP_CONCAT` 을 찾아보세요) → 10단원에서 측정합니다.
5. 태그를 사용자별로 구분해야 한다면(18단원 인증 이후) 어느 테이블에 무엇이 추가될까요? 지금 결정 중 그때 발목을 잡을 것이 있나요?

## 함정

- `PRAGMA foreign_keys = ON` 은 **연결마다** 켜야 합니다. 새 연결을 열고 잊으면 FK 가 조용히 무시되고 CASCADE 도 작동하지 않아
  고아 행(orphan row)이 남습니다. 저장소 생성자에 넣어 둔 이유입니다.
- `JOIN` 뒤에 `WHERE` 로 거르면 **연결이 없는 행은 아예 나오지 않습니다**. "태그가 없는 할 일도 포함해서" 보려면 `LEFT JOIN` 이
  필요합니다. `all()` 에서 태그를 JOIN 으로 한 번에 가져오려 할 때 바로 이 함정에 빠집니다.
- `COUNT(*)` 와 `COUNT(열)` 은 다릅니다. 후자는 NULL 을 세지 않습니다. `LEFT JOIN` + `COUNT(*)` 는 태그 없는 묶음도 1 로 셉니다.
- 복합 기본 키 `(task_id, tag_id)` 는 `task_id` 로 찾을 때는 빠르지만 `tag_id` 만으로 찾을 때는 도움이 안 됩니다(전화번호부가
  성→이름 순일 때 이름만으로 찾는 격). 패턴 B 가 느려지는 이유이고, 10단원의 첫 번째 인덱스가 됩니다.
- 태그 표준화를 저장소마다 따로 구현하면 JSON 과 SQLite 가 서로 다른 태그를 저장하게 됩니다. 규칙은 모델 한 곳(`normalize_tags`)에만.

## 완료 기준

- [ ] `NOTES.md` 에 접근 패턴 표 (코드보다 먼저 작성한 커밋이 남아 있을 것)
- [ ] `pytest units/09-data-modeling` 22개 테스트 전부 통과
- [ ] 테스트를 **2개 직접 추가** (예: 태그 20개를 한 번에 붙이면? `by_tag` 결과의 각 할 일에도 태그 전체가 들어 있는가?)
- [ ] `docs/adr/0003-*.md` — "태그를 별도 테이블(N:M)로 둔다". 대안에 "쉼표 문자열 열", "JSON 배열 열"을 넣고, 접근 패턴 표를 근거로 쓰기
- [ ] `NOTES.md` 에 배운 것 3가지 / 헷갈린 것 1가지 / 다음 단원에 바꿀 것 / 세 문장 설명("왜 태그를 따로 보관하나")
- [ ] AI 코드 리뷰: JOIN 쿼리들을 리뷰받고 하나 반영, 하나 반박
- [ ] 브랜치 `unit-09` → PR → 머지

## 더 깊이

- `all()` 을 쿼리 한 번으로 바꾸기: `LEFT JOIN` + `GROUP_CONCAT(tags.name)` + `GROUP BY tasks.id`. 결과 문자열을 다시 리스트로 쪼개야 합니다. 이 방식의 단점은?
- 정규형(1NF·2NF·3NF)의 교과서 정의를 읽고, `tags_csv` 설계가 몇 정규형을 어기는지 적어 보세요. 반대로 **일부러 비정규화**하는 때는 언제인가요? (읽기가 압도적으로 많고 쓰기가 드물 때 — 19단원 캐싱과 이어집니다)
- 할 일에 "프로젝트"(1:N — 할 일 하나는 프로젝트 하나에만 속함)를 추가한다면 테이블이 몇 개 필요한가요? N:M 과 어떻게 다른가요?
- SQLite 셸에서 `.schema` 와 `SELECT * FROM task_tags` 를 직접 쳐 보고, 연결 테이블이 "사실의 목록"일 뿐임을 눈으로 확인하세요.
