CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL
);

INSERT INTO posts (id, title, body)
OVERRIDING SYSTEM VALUE
VALUES
    (1, '첫 번째 공지', '새 프로젝트를 시작합니다.'),
    (2, '실습 안내', '게시글 번호를 바꿔 보세요.')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('posts', 'id'), COALESCE(MAX(id), 1), true)
FROM posts;
