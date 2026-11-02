"""lost update 를 눈으로 보는 시연. TODO 는 없습니다. 테스트를 통과시킨 뒤 실행해 보세요.

실행: python units/11-transactions-and-concurrency/race_demo.py

스레드 10개가 같은 할 일의 제목 끝에 자기 글자를 하나씩 붙입니다. 모두 성공하면 제목은 10글자가
늘어야 합니다. 실제로는? 그리고 version 검사를 켜면?
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from todo.storage_sqlite import ConflictError, SqliteTaskStore  # noqa: E402

N = 10


def run(use_version: bool) -> tuple[str, int]:
    path = Path(tempfile.mkdtemp()) / "race.db"
    setup = sqlite3.connect(path)
    SqliteTaskStore(setup).init_schema()
    SqliteTaskStore(setup).add("제목:")
    setup.close()

    barrier = threading.Barrier(N)
    conflicts = 0
    lock = threading.Lock()

    def worker(letter: str) -> None:
        nonlocal conflicts
        conn = sqlite3.connect(path, timeout=5)
        store = SqliteTaskStore(conn)
        task = store.get(1)  # 읽고
        barrier.wait()  # 모두 읽을 때까지 기다렸다가
        time.sleep(0.001)
        try:
            if use_version:
                store.rename(1, task.title + letter, expected_version=task.version)
            else:
                store.rename(1, task.title + letter)  # 쓴다
        except ConflictError:
            with lock:
                conflicts += 1
        finally:
            conn.close()

    threads = [threading.Thread(target=worker, args=(chr(ord("A") + i),)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    (title,) = sqlite3.connect(path).execute("SELECT title FROM tasks WHERE id = 1").fetchone()
    return title, conflicts


if __name__ == "__main__":
    title, _ = run(use_version=False)
    print(f"version 검사 없음 → 제목 {title!r}: {N}개 중 {len(title) - 3}개만 남고 나머지는 조용히 사라졌다")
    title, conflicts = run(use_version=True)
    print(f"version 검사 있음 → 제목 {title!r}: 1개 성공, {conflicts}개는 ConflictError 로 '다시 시도하라'는 신호를 받았다")
