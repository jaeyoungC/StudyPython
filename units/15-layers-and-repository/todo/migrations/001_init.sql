-- 08~11단원: 할 일, 태그, 연결 테이블, 인덱스, 낙관적 잠금용 version 열
CREATE TABLE tasks (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    title   TEXT    NOT NULL CHECK (length(trim(title)) > 0),
    done    INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1)),
    version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE tags (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
CREATE INDEX idx_tasks_done ON tasks(done);
CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);
