-- monitor_db에서 실행합니다. 기존 감시 기록을 보존합니다.
CREATE TABLE IF NOT EXISTS http_events (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    attempted_username TEXT,
    source_event_id TEXT
);

ALTER TABLE http_events ADD COLUMN IF NOT EXISTS attempted_username TEXT;
ALTER TABLE http_events ADD COLUMN IF NOT EXISTS source_event_id TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS http_events_source_event_id_unique
    ON http_events (source_event_id);

CREATE TABLE IF NOT EXISTS detection_observations (
    sequence BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id TEXT UNIQUE NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    after_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL
);

