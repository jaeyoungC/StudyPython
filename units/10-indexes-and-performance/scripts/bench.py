"""10단원 벤치마크: 인덱스가 조회와 쓰기에 미치는 영향을 숫자로 본다.

실행 (저장소 루트에서):
    python units/10-indexes-and-performance/scripts/bench.py            # 기본 10만 건
    python units/10-indexes-and-performance/scripts/bench.py --tasks 20000

측정 결과를 README 의 측정표 형식으로 NOTES.md 에 옮겨 적으세요.
숫자는 컴퓨터마다 다릅니다. 중요한 것은 절대값이 아니라 **배율**과 **방향**입니다.
"""

from __future__ import annotations

import argparse
import random
import sqlite3
import sys
import time
from pathlib import Path
from typing import Callable

# 이 파일은 `scripts/` 안에 있어서 그대로 실행하면 `todo` 패키지를 찾지 못한다. 단원 폴더를 경로에 더한다.
UNIT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(UNIT_DIR))

from todo.storage_sqlite import SqliteTaskStore  # noqa: E402  (경로 설정 뒤에 import)

TAG_INDEX = "idx_task_tags_tag"
BY_TAG_SQL = """
SELECT tasks.id, tasks.title, tasks.done
FROM tasks
JOIN task_tags ON task_tags.task_id = tasks.id
JOIN tags      ON tags.id = task_tags.tag_id
WHERE tags.name = ?
ORDER BY tasks.id
"""
OPEN_SQL = "SELECT id, title, done FROM tasks WHERE done = 0 ORDER BY id"


def generate(conn: sqlite3.Connection, n_tasks: int, n_tags: int, rng: random.Random) -> None:
    """할 일 n_tasks 개와 태그 n_tags 종류를 만들고, 할 일마다 태그 1~3개를 붙인다.

    `executemany` 는 같은 SQL 을 여러 값으로 반복 실행한다. 파이썬 루프에서 `execute` 를 n 번 부르는 것보다
    훨씬 빠르다. 전체를 트랜잭션 하나로 묶기 위해 마지막에 한 번만 commit 한다 (11단원에서 왜 빠른지 배운다).
    """
    conn.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        ((f"할 일 {i}", 1 if rng.random() < 0.2 else 0) for i in range(n_tasks)),
    )
    conn.executemany("INSERT INTO tags (name) VALUES (?)", ((f"tag{i:03d}",) for i in range(n_tags)))
    links = set()
    for task_id in range(1, n_tasks + 1):
        for _ in range(rng.randint(1, 3)):
            links.add((task_id, rng.randint(1, n_tags)))
    conn.executemany("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", sorted(links))
    conn.commit()


def measure(fn: Callable[[], object], repeat: int = 5) -> float:
    """fn 을 repeat 번 실행한 평균 시간(밀리초).

    `time.perf_counter()` 는 벽시계(`time.time`)보다 정밀한 "경과 시간 측정용" 시계다. 두 번 읽어 빼면 초 단위 경과 시간.
    """
    # TODO
    raise NotImplementedError


def plan(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> str:
    """EXPLAIN QUERY PLAN 결과의 detail 열(각 행의 4번째 값)을 " | " 로 이어 붙여 돌려준다.

    힌트: SQL 문자열 앞에 "EXPLAIN QUERY PLAN " 을 붙여 실행하면 결과 행마다 (id, parent, notused, detail) 이 나온다.
    """
    # TODO
    raise NotImplementedError


def fresh_db(n_tasks: int, n_tags: int, seed: int, with_index: bool) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    store = SqliteTaskStore(conn)
    store.init_schema()
    if not with_index:
        conn.execute(f"DROP INDEX IF EXISTS {TAG_INDEX}")
    generate(conn, n_tasks, n_tags, random.Random(seed))
    return conn


def bench_by_tag(conn: sqlite3.Connection, tag: str) -> float:
    return measure(lambda: conn.execute(BY_TAG_SQL, (tag,)).fetchall())


def bench_open_tasks(conn: sqlite3.Connection) -> float:
    return measure(lambda: conn.execute(OPEN_SQL).fetchall(), repeat=3)


def bench_insert(conn: sqlite3.Connection, n: int, rng: random.Random) -> float:
    """할 일 n 개를 태그 하나씩 붙여 추가하는 데 걸리는 시간. 인덱스가 있으면 INSERT 마다 인덱스도 갱신해야 한다."""
    store = SqliteTaskStore(conn)
    # TODO: store.add(...) 를 n 번 부르는 함수를 만들어 measure(..., repeat=1) 로 재서 돌려준다.
    #   태그는 f"tag{rng.randint(0, 49):03d}" 처럼 rng 로 고른다 (난수는 인자로 주입 — 테스트 규약).
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="인덱스 벤치마크")
    parser.add_argument("--tasks", type=int, default=100_000)
    parser.add_argument("--tags", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    results: dict[str, dict[bool, float]] = {"by_tag 조회": {}, "open_tasks 조회": {}, "INSERT 2000건(태그 포함)": {}}
    plans: dict[bool, str] = {}
    for with_index in (False, True):
        conn = fresh_db(args.tasks, args.tags, args.seed, with_index)
        plans[with_index] = plan(conn, BY_TAG_SQL, ("tag007",))
        results["by_tag 조회"][with_index] = bench_by_tag(conn, "tag007")
        results["open_tasks 조회"][with_index] = bench_open_tasks(conn)
        results["INSERT 2000건(태그 포함)"][with_index] = bench_insert(conn, 2000, random.Random(args.seed))
        conn.close()

    print(f"\n할 일 {args.tasks:,}건, 태그 {args.tags}종류, 인덱스 = {TAG_INDEX}\n")
    print("| 작업 | 인덱스 없음 (ms) | 인덱스 있음 (ms) | 있음/없음 |")
    print("| --- | --- | --- | --- |")
    for name, by_index in results.items():
        without, with_ = by_index[False], by_index[True]
        ratio = with_ / without if without else float("nan")
        print(f"| {name} | {without:.2f} | {with_:.2f} | x{ratio:.2f} |")
    print("\n쿼리 플랜 (by_tag):")
    print(f"- 인덱스 없음: {plans[False]}")
    print(f"- 인덱스 있음: {plans[True]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
