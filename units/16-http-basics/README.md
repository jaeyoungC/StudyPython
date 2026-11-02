# 16 — HTTP 기초

## 목표

HTTP 요청과 응답이 **텍스트 몇 줄**이라는 것을 `curl` 로 눈으로 확인하고, 프레임워크 없이 표준 라이브러리
`http.server` 만으로 15단원의 `TaskService` 를 HTTP 로 노출합니다. 이 단원이 끝나면 17단원에서 FastAPI 가
"대신 해 주는 일"이 정확히 무엇인지 알게 됩니다.

## 노트와의 연결

노트는 풀스택 기초 항목으로 "**API 선택과 설계**"를 꼽습니다. API 를 설계하려면 먼저 API 가 **무엇으로 만들어져
있는지** 알아야 합니다. 메서드·경로·상태 코드·헤더·본문, 이 다섯 가지가 전부이고, 이 단원은 그 다섯 가지를 직접
읽고 직접 씁니다. 또 노트는 "에이전트는 사람보다 훨씬 많이 호출한다"고 합니다. 에이전트가 호출하는 것도 결국 이 다섯 가지입니다.

## 공부할 개념

| 개념 | 핵심 | 참고 |
| --- | --- | --- |
| 요청·응답의 구조 | 요청 = 시작 줄(`GET /tasks HTTP/1.1`) + 헤더 + 빈 줄 + 본문. 응답 = 상태 줄(`HTTP/1.1 200 OK`) + 헤더 + 빈 줄 + 본문. `Content-Type` 은 본문의 형식, `Content-Length` 는 본문의 길이 | [MDN: HTTP 개요](https://developer.mozilla.org/ko/docs/Web/HTTP/Overview), [MDN: HTTP 메시지](https://developer.mozilla.org/ko/docs/Web/HTTP/Messages) |
| 메서드와 상태 코드 | `GET` 읽기(안전·멱등), `POST` 만들기/행동, `DELETE` 지우기(멱등). 2xx 성공, 4xx 호출자 잘못(400 형식, 404 없음, 409 상태 충돌, 422 내용 검증 실패), 5xx 서버 잘못 | [MDN: 요청 메서드](https://developer.mozilla.org/ko/docs/Web/HTTP/Methods), [MDN: 상태 코드](https://developer.mozilla.org/ko/docs/Web/HTTP/Status) |
| `http.server` 와 `urllib.request` | 요청마다 핸들러 클래스가 인스턴스화되고 `do_GET` 같은 메서드가 불린다. 클라이언트 쪽은 `urllib.request.urlopen` 으로 충분하다 | [http.server](https://docs.python.org/ko/3/library/http.server.html), [urllib.request](https://docs.python.org/ko/3/library/urllib.request.html) |

처음 보는 표준 라이브러리 두 가지만 더: `urllib.parse.urlsplit` / `parse_qs` 는 `/tasks/3?done=true` 를 경로와 쿼리로 나눕니다.
`http.HTTPStatus.NOT_FOUND` 는 그냥 `404` 입니다. 숫자 대신 이름을 쓰면 코드가 문서가 됩니다.

테스트는 서버를 **별도 스레드**(11단원에서 썼던 `threading.Thread`)에서 `port=0` 으로 띄웁니다. 0을 주면 운영체제가 빈 포트를 골라 주어
테스트가 서로, 또 내가 띄워 둔 서버와 부딪히지 않습니다.

## 과제

### 1부 — 손으로 HTTP 보내 보기 (코드 없음, 결과를 NOTES.md 에 붙이기)

공개 연습용 서버 [httpbin.org](https://httpbin.org) 에 `curl` 로 요청을 보냅니다. (`-i` 응답 헤더 포함, `-v` 요청까지 전부, `-X` 메서드, `-H` 헤더, `-d` 본문)

```sh
curl -i https://httpbin.org/get                       # 상태 줄과 헤더를 읽어 보세요
curl -v https://httpbin.org/get 2>&1 | grep '^[<>]'   # > 가 내가 보낸 것, < 가 받은 것
curl -i -X POST -H 'Content-Type: application/json' -d '{"title":"산책"}' https://httpbin.org/post
curl -i https://httpbin.org/status/404                # 본문 없는 404
curl -i https://httpbin.org/status/500
curl -i -H 'Accept: application/xml' https://httpbin.org/get   # 헤더가 응답을 바꾸는가?
```

각 명령에 대해 **상태 코드, `Content-Type`, 본문 첫 줄**을 적습니다. 인터넷이 안 되면 2부의 서버를 먼저 띄우고 같은 연습을 하세요.

### 2부 — 최소 서버 완성하기

`todo/simple_http.py` 의 `_handle` 과 `_parse_done` 의 `TODO` 를 채워 `pytest units/16-http-basics` 를 통과시키세요.
응답 쓰기(`_send_json`), 본문 읽기(`_read_json`), 예외 → 상태 코드 번역(`_dispatch`)은 이미 있습니다. 여러분이 쓰는 것은 **라우팅**(경로·메서드 → 서비스 호출)입니다.

| 메서드 · 경로 | 응답 | 테스트 |
| --- | --- | --- |
| `GET /health` | 200 `{"status":"ok"}` (완성되어 있음) | `test_health_*` |
| `GET /tasks?done=` | 200 할 일 배열 (`done` 없으면 전체) | `test_get_list_*` |
| `POST /tasks` | 201 Task / 422 빈 제목 / 400 JSON 아님 | `test_post_*` |
| `GET /tasks/{id}` | 200 / 404 | `test_get_one_*` |
| `POST /tasks/{id}/complete` | 200 / 404 / 409 | `test_complete_*` |
| `DELETE /tasks/{id}` | 204 본문 없음 / 404 | `test_delete_*` |
| 그 밖에 | 404 `{"error":{"code":"not_found",...}}` | `test_unknown_path_*` |

다 되면 `python -m todo.simple_http` 로 띄우고 1부의 `curl` 명령을 내 서버에 그대로 보내 보세요. `curl -i -X DELETE http://127.0.0.1:8000/tasks/1` 의 응답에 본문이 없는 것을 확인하세요.

구현 전에는 테스트가 `RemoteDisconnected` 로 실패합니다. 핸들러 안에서 예외가 나면 `http.server` 가 응답 없이 연결을 끊기 때문입니다. 서버 터미널의 트레이스백을 보세요.

## 스스로 답해 볼 질문

1. `POST /tasks/{id}/complete` 는 왜 `PUT /tasks/{id}` 에 `{"done": true}` 를 보내는 것과 다른가요? 같은 요청을 두 번 보내면 각각 무슨 일이 일어나야 하나요?
2. 빈 제목은 422, JSON 이 아닌 본문은 400, 이미 완료는 409, 없는 id는 404 입니다. 이 넷을 모두 400 하나로 돌려주면 호출자(사람·화면·에이전트)는 무엇을 잃나요?
3. `DELETE` 를 두 번 보내면 두 번째는 404 입니다. 204 를 돌려주는 설계도 있습니다. 어느 쪽이 "멱등"에 가깝고, 어느 쪽이 호출자에게 더 많은 정보를 주나요? → 26단원
4. 서버는 요청마다 새 스레드를 씁니다(`ThreadingHTTPServer`). `MemoryTaskRepository` 의 리스트에 두 스레드가 동시에 `append` 하면 11단원의 lost update 가 날 수 있나요? SQLite 리포지토리를 꽂으면 어떻게 될까요?
5. 응답에 `Content-Length` 를 틀리게 쓰면 클라이언트는 어떻게 되나요? (실험해 보세요. `_send_json` 의 길이에 +1 을 하고 `curl` 로.)

## 함정

- `self.path` 에는 쿼리 문자열이 붙어 있습니다(`/tasks?done=true`). 경로 비교 전에 `urlsplit` 으로 나누세요.
- `Content-Length` 없이 본문을 읽으려 `self.rfile.read()` 를 부르면 클라이언트가 연결을 닫을 때까지 **멈춥니다**. 길이만큼만 읽으세요.
- 204 응답에 본문을 쓰면 일부 클라이언트가 다음 응답으로 착각합니다. `_send_json(204)` 처럼 본문 없이 보내세요.
- `urllib` 은 4xx/5xx 에서 `HTTPError` 예외를 던집니다. 그 예외 객체는 응답처럼 `.read()` 할 수 있습니다. 테스트의 `call` 도우미가 그렇게 합니다.
- 테스트 픽스처에서 `server.shutdown()` 을 빼먹으면 스레드가 남아 다음 테스트의 포트와는 안 부딪혀도(0 포트) 프로세스가 지저분하게 끝납니다.

## 완료 기준

- [ ] 1부: 여섯 `curl` 명령의 상태 코드·`Content-Type`·본문 첫 줄을 `NOTES.md` 에 표로
- [ ] `pytest units/16-http-basics` 12개 테스트 전부 통과
- [ ] 테스트 **1개 직접 추가**: `GET /tasks/abc` (숫자가 아닌 id) 는 몇 번이어야 하나요? 먼저 정하고 테스트로 적기
- [ ] `python -m todo.simple_http` 를 띄우고 `curl` 로 add → complete → complete(409) → delete(204) 를 한 번씩
- [ ] `NOTES.md`: 배운 것 3가지 / 헷갈린 것 1가지 / 다음 단원에 바꿀 것, **세 문장 설명**("상태 코드가 왜 여러 개인지")
- [ ] **AI 코드 리뷰**: `_handle` 을 리뷰받고 지적 하나 반영, 하나 반박
- [ ] **에이전트에게 작은 과제**: `GET /tasks/search?q=` 경로 추가(서비스의 `search` 호출). 맡기기 전에 테스트를 **내가** 먼저 쓰고, 에이전트는 그 테스트를 통과시키게 하세요. 에이전트가 테스트를 고치려 하면 거부하세요
- [ ] 브랜치 `unit-16` → PR → 머지 (이 단원은 설계 결정이 작아 ADR 은 선택)

## 더 깊이

- `curl -v` 출력에서 `Connection: keep-alive` 를 찾아보세요. HTTP/1.1 은 한 연결로 여러 요청을 보냅니다. `http.server` 의 `protocol_version` 을 `"HTTP/1.1"` 로 바꾸면 무엇이 달라지나요?
- [MDN: HTTP 캐싱](https://developer.mozilla.org/ko/docs/Web/HTTP/Caching) 을 훑어 두세요. 19단원에서 `ETag` 를 직접 만듭니다.
- 시간을 내서 `nc -l 8001` 로 "서버 없는 포트"를 열고 `curl http://127.0.0.1:8001/x` 를 보내 보세요. 요청이 날것 그대로 보입니다.
