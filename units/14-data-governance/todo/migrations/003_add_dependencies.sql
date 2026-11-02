-- 003: 할 일 사이의 의존 관계 (그래프의 간선). "task_id 는 depends_on 이 끝나야 시작할 수 있다".
CREATE TABLE IF NOT EXISTS task_deps (
    task_id    INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, depends_on),
    CHECK (task_id <> depends_on)
);

-- "이 할 일을 기다리는 것은 무엇인가" (역방향 탐색) 를 위한 인덱스. PK 는 task_id 먼저라 depends_on 만으로는 못 쓴다 (10단원).
CREATE INDEX IF NOT EXISTS idx_task_deps_depends_on ON task_deps (depends_on);
