-- 감시 앱 배포 SQL
-- Neon 감시 DB에 직접 실행합니다. 기존 테이블·자료를 지우지 않습니다.
-- Neon 콘솔 > SQL Editor 또는 psql로 실행하세요.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS http_events (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    attempted_username TEXT
);

ALTER TABLE http_events ADD COLUMN IF NOT EXISTS attempted_username TEXT;

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL
);

