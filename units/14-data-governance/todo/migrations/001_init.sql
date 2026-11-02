-- 001: 11단원까지의 스키마 전체.
-- IF NOT EXISTS 를 쓰는 이유: 마이그레이션 도입 전에 init_schema() 로 만든 DB(user_version = 0) 에도
-- 그대로 적용할 수 있어야 하기 때문이다. 이미 있는 테이블은 건드리지 않고 번호만 1 로 올라간다.

CREATE TABLE IF NOT EXISTS tasks (
    id      INTEGER PRIMARY KEY,
    title   TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    done    INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tags (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_task_tags_tag ON task_tags (tag_id);
