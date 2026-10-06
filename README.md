# Mini Watch · Day5 시작 자료

Day4 React 수업과 일반 게시판 부록까지 마친 완성 코드다. 일반 서비스와 감시 서비스는 각각 React frontend, Flask backend, PostgreSQL DB를 사용한다.

## 저장소와 별도 작업 폴더

먼저 https://github.com/zeroskill2400/mini-watch/tree/day05-start 를 확인한다. 기존 Day3·Day4 폴더는 보존하고 새 작업 폴더로 받는다.

```text
git clone --branch day05-start --single-branch https://github.com/zeroskill2400/mini-watch.git mini-watch-day05
```

## 실행 준비

VS Code에서 이 폴더를 연다. 터미널 기본 프로필은 Command Prompt(CMD)로 선택한 뒤 새 터미널을 연다. 기존 5100·5200·5173·5174 서버가 있다면 Ctrl+C로 종료한다.

1. general/backend와 monitor/backend 각각에서 CMD를 열고 Python 환경을 준비한다.

```text
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

2. 각 backend의 .env.example을 같은 폴더에 복사하여 .env로 바꾼다. 기존 PostgreSQL 접속 정보를 넣고 DB_NAME은 일반 general_db, 감시 monitor_db를 유지한다. Day4에서 사용한 각 서비스의 SECRET_KEY를 해당 .env로 복사한다. 처음 만들 때만 아래 명령으로 서로 다른 값을 생성하고 .env에 넣는다. .env는 Git에 올리지 않는다.

```text
python -c "import secrets; print(secrets.token_hex(32))"
```

3. Day4의 DB와 계정을 준비했다면 기존 DB를 재사용한다. 새 DB에서 시작하는 경우 pgAdmin으로 general/backend/sql/create_database.sql과 monitor/backend/sql/create_database.sql을 postgres DB에서 각각 실행해 DB를 만든다. 각 DB의 Query Tool에서 해당 backend/sql/day04.sql을 실행한다. 두 backend에서 python create_user.py를 실행하면 공개 수업 계정이 만들어진다. 이미 있는 계정은 비밀번호를 덮어쓰지 않는다.

4. 두 backend의 활성화된 CMD에서 각각 python app.py를 실행한다.

5. general/frontend와 monitor/frontend 각각의 별도 CMD에서 실행한다.

```text
npm ci
npm run dev
```

| 서비스 | React | Flask | 수업용 계정 |
|---|---|---|---|
| 일반 게시판 | http://127.0.0.1:5174 | http://127.0.0.1:5100 | student / Learn123! |
| 감시 대시보드 | http://127.0.0.1:5173 | http://127.0.0.1:5200 | operator / Learn123! |

Node.js는 Node 24 LTS 계열을 사용한다. Vite와 React의 버전은 package.json과 package-lock.json에 고정되어 있다. React는 /api 개발 프록시로 자기 Flask와 통신한다. Flask는 .env를 자기 파일 옆에서 읽는다.

## 확인 순서

일반 React 게시판에서 로그인 → 글 작성 → 상세 → 수정 → 삭제를 확인한다. 5100의 Jinja2 비교 화면도 같은 posts를 읽는다. 감시 React에서 운영자로 로그인 → 기록 조회 → 관찰 메모 CRUD를 확인한다. 새로고침 후 로그인 유지와 로그아웃도 확인한다.

원본 요청 기록은 읽기 자료이며 메모와 별도다. POST /api/events는 기존 수업용 서버 간 수집 경로다. 감시 서비스가 일반 서비스의 로그인이나 게시글 요청을 중계하지 않는다.

## 파일 역할

frontend/src/components는 화면, frontend/src/api는 JSON 요청을 맡는다. backend/routes는 HTTP, backend/repositories는 SQL, backend/db.py는 PostgreSQL 연결을 맡는다. Python 쿠키 이름은 general_session과 monitor_session으로 나누었다.

try_*.py는 앞 수업의 연습 이력이다. 오늘의 인증 이전 방식도 포함하므로 현재 동작 확인은 React 화면과 Day4 교안을 사용한다. .env, venv, node_modules, dist는 저장소에 포함하지 않는다.
