"""표준 라이브러리 http.server 만으로 만든 최소 HTTP 서버 (16단원).

프레임워크 없이 "요청 한 줄 + 헤더 + 본문"을 직접 읽고 "상태 줄 + 헤더 + 본문"을 직접 씁니다.
17단원에서 FastAPI 가 대신해 주는 일이 정확히 무엇인지 몸으로 알기 위한 코드입니다.

실행: python -m todo.simple_http  (메모리 저장소, 127.0.0.1:8000)
확인: curl -i http://127.0.0.1:8000/health

경로 규칙 (docs/project-api.md 의 17단원 표와 같다, 페이지네이션만 아직 없다):
    GET    /health              200 {"status": "ok"}
    GET    /tasks[?done=false]  200 [Task, ...]
    POST   /tasks               201 Task      (본문 {"title": "...", "tags": [...]})   422 빈 제목
    GET    /tasks/{id}          200 Task      404
    POST   /tasks/{id}/complete 200 Task      404 / 409 이미 완료
    DELETE /tasks/{id}          204 (본문 없음) 404
    그 밖의 경로                 404
오류 본문은 항상 {"error": {"code": "...", "message": "..."}} 입니다.
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .models import TaskNotFoundError
from .repository import MemoryTaskRepository
from .service import AlreadyDoneError, TaskService


class BadRequest(Exception):
    """본문이 JSON 이 아니거나 형식이 틀렸을 때 → 400."""


def make_handler(service: TaskService) -> type[BaseHTTPRequestHandler]:
    """service 를 닫아 넣은(closure) 핸들러 클래스를 만든다.

    http.server 는 요청마다 핸들러 *클래스*를 인스턴스화하므로, 인스턴스에 서비스를 넘길 방법이 없다.
    대신 클래스를 그때그때 만들어 서비스를 클래스 속성으로 붙인다.
    """

    class TodoHandler(BaseHTTPRequestHandler):
        # --- 도우미: 그대로 쓰면 됩니다 -------------------------------------

        def log_message(self, format: str, *args) -> None:  # 테스트 출력이 지저분해지지 않도록 끈다
            pass

        def _send_json(self, status: int, body: object | None = None) -> None:
            """상태 줄, 헤더, 본문 순서로 쓴다. 본문이 없으면(204) 헤더만 보낸다."""
            payload = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            if payload:
                self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            if payload:
                self.wfile.write(payload)

        def _send_error(self, status: int, code: str, message: str) -> None:
            self._send_json(status, {"error": {"code": code, "message": message}})

        def _read_json(self) -> dict:
            """Content-Length 만큼 읽어 JSON 으로 푼다. 틀리면 BadRequest."""
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b""
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise BadRequest(f"본문이 올바른 JSON 이 아닙니다: {error}") from error
            if not isinstance(data, dict):
                raise BadRequest("본문은 JSON 객체여야 합니다")
            return data

        def _route(self) -> tuple[list[str], dict[str, list[str]]]:
            """'/tasks/3/complete?x=1' → (['tasks', '3', 'complete'], {'x': ['1']})"""
            parts = urlsplit(self.path)
            segments = [s for s in parts.path.split("/") if s]
            return segments, parse_qs(parts.query)

        def _dispatch(self, method: str) -> None:
            """예외를 상태 코드로 번역하는 한 곳. 각 do_* 는 여기로 들어온다."""
            try:
                self._handle(method)
            except BadRequest as error:
                self._send_error(HTTPStatus.BAD_REQUEST, "bad_request", str(error))
            except TaskNotFoundError as error:
                self._send_error(HTTPStatus.NOT_FOUND, "not_found", str(error))
            except AlreadyDoneError as error:
                self._send_error(HTTPStatus.CONFLICT, "already_done", str(error))
            except ValueError as error:
                self._send_error(HTTPStatus.UNPROCESSABLE_CONTENT, "validation_error", str(error))

        def do_GET(self) -> None:
            self._dispatch("GET")

        def do_POST(self) -> None:
            self._dispatch("POST")

        def do_DELETE(self) -> None:
            self._dispatch("DELETE")

        # --- 과제: 경로와 메서드를 보고 서비스를 호출해 응답을 만든다 ------------

        def _handle(self, method: str) -> None:
            segments, query = self._route()
            if segments == ["health"] and method == "GET":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if segments == ["tasks"]:
                if method == "GET":
                    done = _parse_done(query.get("done", [None])[0])
                    self._send_json(HTTPStatus.OK, [t.to_dict() for t in service.list(done=done)])
                    return
                if method == "POST":
                    data = self._read_json()
                    title = data.get("title")
                    if not isinstance(title, str):
                        raise BadRequest("title 은 문자열이어야 합니다")
                    task = service.add(title, tags=data.get("tags", []))
                    self._send_json(HTTPStatus.CREATED, task.to_dict())
                    return
            if len(segments) >= 2 and segments[0] == "tasks" and segments[1].isdigit():
                task_id = int(segments[1])
                if len(segments) == 2 and method == "GET":
                    self._send_json(HTTPStatus.OK, service.get(task_id).to_dict())
                    return
                if len(segments) == 2 and method == "DELETE":
                    service.remove(task_id)
                    self._send_json(HTTPStatus.NO_CONTENT)
                    return
                if segments[2:] == ["complete"] and method == "POST":
                    self._send_json(HTTPStatus.OK, service.complete(task_id).to_dict())
                    return
            self._send_error(HTTPStatus.NOT_FOUND, "not_found", f"{method} {self.path} 에 해당하는 리소스가 없습니다")

    return TodoHandler


def _parse_done(value: str | None) -> bool | None:
    """쿼리 문자열의 done 값을 bool 로. 없으면 None, 이상한 값이면 BadRequest."""
    if value is None:
        return None
    if value.lower() in ("true", "1"):
        return True
    if value.lower() in ("false", "0"):
        return False
    raise BadRequest(f"done 은 true/false 여야 합니다: {value!r}")


def serve(service: TaskService, host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """서버 객체를 만들어 돌려준다. 실제로 돌리는 것은 호출한 쪽(serve_forever)이다. port=0 이면 빈 포트를 고른다."""
    return ThreadingHTTPServer((host, port), make_handler(service))


if __name__ == "__main__":
    server = serve(TaskService(MemoryTaskRepository()))
    print(f"http://{server.server_address[0]}:{server.server_address[1]}  (Ctrl+C 로 종료)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
