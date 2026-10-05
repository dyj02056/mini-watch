# mini-watch 4일차 시작 코드

GitHub: https://github.com/zeroskill2400/mini-watch

이 자료는 3일차에 완성한 일반 서비스의 게시글 CRUD·로그인 입력 화면과 감시 서비스의 기록 수집·조회 API다. 일반 화면은 Flask와 Jinja2로 만들었고, JavaScript는 기존 로그인 JSON API에 입력을 보내는 데 사용한다. 4일차에는 이 코드를 이어서 감시 화면을 만든다.

수업을 정상적으로 따라왔다면 지금 사용하던 폴더와 DB를 계속 사용한다. 새 PC에서 시작하거나 완성 코드와 비교할 때만 저장소의 `day04-start`를 받는다. 기존 실습 폴더 위에 덮어쓰지 않는다.

```bat
git clone --branch day04-start https://github.com/zeroskill2400/mini-watch.git mini-watch-day04-start
```

Git에는 코드·SQL·설정 예시만 들어 있다. 실제 `.env`, 가상환경, 이미 작성한 게시글과 수집 기록은 함께 오지 않는다.

## 실행 구조

```text
브라우저 → 일반 Flask 5100 → general_db
                  │ 요청 결과(method/path/status_code)
                  └────────→ 감시 Flask 5200 → monitor_db
```

일반 화면은 5100으로 접속한다. 감시 서비스는 일반 서비스가 보낸 기록을 수집하고 조회한다. 일반 사용자의 요청을 대신 전달하는 게이트웨이가 아니다.

## 폴더

```text
mini-watch-day04-start/
├─ .gitignore
├─ README.md
├─ general/
│  ├─ app.py
│  ├─ db.py
│  ├─ post_rules.py
│  ├─ requirements.txt
│  ├─ .env.example
│  ├─ create_user.py
│  ├─ try_db.py
│  ├─ try_hash.py
│  ├─ try_login.py
│  ├─ try_record.py
│  ├─ try_send_event.py
│  ├─ try_events.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  ├─ posts.py
│  │  └─ auth.py
│  ├─ templates/
│  │  ├─ index.html
│  │  ├─ detail.html
│  │  ├─ error.html
│  │  ├─ new.html
│  │  ├─ edit.html
│  │  ├─ delete.html
│  │  └─ login.html
│  ├─ static/
│  │  ├─ style.css
│  │  └─ login.js
│  └─ sql/
│     ├─ create_database.sql
│     ├─ posts.sql
│     ├─ post_ids.sql
│     └─ users.sql
└─ monitor/
   └─ backend/
      ├─ app.py
      ├─ db.py
      ├─ requirements.txt
      ├─ .env.example
      ├─ try_event.py
      └─ sql/
         ├─ create_database.sql
         └─ http_events.sql
```

`app.py`는 앱을 만들고 두 Blueprint를 등록하며 공통 요청 기록을 남긴다. 게시글 경로는 `routes/posts.py`, 로그인 경로는 `routes/auth.py`에 있다. `post_rules.py`는 작성·수정에서 함께 사용하는 입력 검사 함수다. `db.py`의 연결 함수와 `templates`, `static`, `sql`의 위치는 그대로다.

## 1. Windows 터미널과 패키지 준비

Python과 PostgreSQL이 설치된 PC에서 VS Code로 프로젝트 폴더를 연다. `Ctrl+Shift+P` → `Terminal: Select Default Profile` → **Command Prompt(CMD, 명령 프롬프트)**를 선택하고 새 터미널을 연다. 기존 터미널의 종류는 자동으로 바뀌지 않는다.

VS Code에서 `general` 폴더를 오른쪽 클릭해 통합 터미널을 연다. 새로 받은 폴더에서는 처음 한 번 가상환경을 만든다.

```bat
python -m venv venv
```

가상환경을 켠다. 입력 줄 앞에 `(venv)`가 붙는지 확인한다.

```bat
venv\Scripts\activate
```

패키지를 설치한다.

```bat
python -m pip install -r requirements.txt
```

`monitor/backend` 폴더에서도 새 CMD를 열고 같은 순서로 그 폴더의 가상환경과 패키지를 준비한다. 두 폴더는 각각의 `requirements.txt`를 사용한다.

## 2. DB 접속 설정

`general/.env.example`을 같은 폴더에 `.env`라는 이름으로 저장하고 자기 PC의 DB 접속 값을 입력한다. `DB_NAME`은 `general_db`다.

`monitor/backend/.env.example`도 같은 폴더의 `.env`로 저장한다. 감시 서비스의 `DB_NAME`은 `monitor_db`다. 실제 비밀번호가 들어 있는 `.env`는 Git에서 제외한다.

## 3. 새 PC의 DB 준비

이미 사용 중인 DB와 게시글이 있으면 초기 테이블·게시글 SQL을 다시 실행하지 않는다. 새 PC에서는 pgAdmin의 Query Tool에서 다음 순서로 실행한다.

1. `postgres` DB에서 `general/sql/create_database.sql` 실행.
2. `general_db`의 Query Tool을 새로 열고 `SELECT current_database();`로 연결 확인.
3. `general/sql/posts.sql` 실행: 게시글 테이블과 초기 글 두 건 생성.
4. `general/sql/post_ids.sql` 실행: 새 게시글 번호를 PostgreSQL이 발급하도록 설정.
5. `general/sql/users.sql` 실행: 사용자 테이블 생성.

`post_ids.sql`은 일반 서버를 중지한 상태에서 실행한다. 기존 글을 지우지 않고, 현재 글 번호와 시퀀스의 마지막 번호 중 큰 값에서 이어 간다. 번호에는 빈 값이 생길 수 있으며 글 개수를 뜻하지 않는다. 이전 단계 DB를 쓰는 경우 이 준비를 아직 하지 않았을 때만 추가한다.

`general` 폴더에서 가상환경이 켜진 CMD로 실습 계정을 만든다.

```bat
python create_user.py
```

실습용 아이디는 `student`, 비밀번호는 `Learn123!`다. 같은 아이디가 이미 있으면 기존 계정을 유지한다. 이 값은 수업을 위한 공개 예시다.

감시 DB도 새로 준비한다.

1. `postgres` DB에서 `monitor/backend/sql/create_database.sql` 실행.
2. `monitor_db`의 Query Tool을 새로 열고 `SELECT current_database();`로 연결 확인.
3. `monitor/backend/sql/http_events.sql` 실행.

## 4. 서버 실행

감시 서버부터 실행한다. `monitor/backend` 폴더에서 CMD를 열고 가상환경을 켠다.

```bat
venv\Scripts\activate
```

그다음 서버를 실행한다.

```bat
python app.py
```

일반 서버는 `general` 폴더에서 별도의 CMD를 열어 실행한다. 먼저 가상환경을 켠다.

```bat
venv\Scripts\activate
```

그다음 서버를 실행한다.

```bat
python app.py
```

서버 코드를 바꾸면 해당 서버의 CMD에서 `Ctrl+C`로 중지한 뒤 `python app.py`로 다시 실행한다. 서버가 실행 중인 창에는 다른 명령을 입력하지 않는다.

## 5. 화면과 요청 기록 확인

크롬 주소창에 http://127.0.0.1:5100/ 을 입력한다.

- 목록의 게시글을 누르면 `/board/번호`에서 내용을 읽는다.
- 새 게시글을 작성하면 POST 요청으로 DB에 저장하고 303 응답으로 상세 페이지로 이동한다.
- 수정 화면에서 저장하면 같은 번호의 제목·내용이 바뀐다.
- 삭제 화면을 여는 것만으로는 지워지지 않는다. 삭제 확인 버튼의 POST 요청으로 지운다.
- 제목이나 내용이 비어 있으면 400 응답과 안내가 나오고 DB는 바뀌지 않는다.

http://127.0.0.1:5100/login 에서 실습용 아이디·비밀번호를 입력한다. JavaScript가 기존 `/auth/login`에 JSON을 보내고 결과 문구를 화면에 표시한다. 성공·실패를 판정하는 실습이며 로그인 상태 유지와 게시글 접근 제한은 아직 만들지 않았다. 게시글 CRUD는 로컬 교실 실습용 공개 기능이다.

기존 JSON 조회 주소 http://127.0.0.1:5100/posts/1 도 그대로 사용할 수 있다.

감시 기록은 아래 주소에서 확인한다.

- http://127.0.0.1:5200/health
- http://127.0.0.1:5200/api/events
- http://127.0.0.1:5200/api/events?event_type=login_failure

일반 서버는 메서드·경로·상태 코드만 기록으로 보낸다. 비밀번호와 요청 본문은 보내지 않는다. HTML 조회·CSS·JavaScript 조회·303 이동 응답도 기록될 수 있어, 화면을 한 번 열었다고 기록이 반드시 한 건만 생기는 것은 아니다.

감시 서버는 최근 50건을 반환한다. `occurred_at`은 감시 DB에 저장한 시각이다. 전송 실패 시 일반 응답은 유지하지만 해당 기록은 누락될 수 있으며 재전송 기능은 없다.

두 서비스와 DB를 그대로 두고 4일차 감시 화면 작업을 이어 간다.
