-- 18단원: 할 일의 소유자 (users 는 아직 메모리에만 있으므로 FK 없이 정수 id 만 둔다)
ALTER TABLE tasks ADD COLUMN owner_id INTEGER;
CREATE INDEX idx_tasks_owner ON tasks(owner_id);
