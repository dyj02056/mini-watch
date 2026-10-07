# Mini Watch 감시 대시보드 (Day04)

React 대시보드와 Flask API를 연결하여 일반 서비스의 요청 기록을 실시간 모니터링하고, 운영자가 관찰 메모를 관리할 수 있는 모니터링 시스템입니다.

---

## 1. 프로젝트 개요 및 아키텍처

- **일반 서비스 (`general/`)**: 게시판 기능 제공 및 HTTP 요청/이벤트 로그를 감시 서비스로 전송 (`http://127.0.0.1:5100`)
- **감시 API (`monitor/backend/`)**: Flask 기반 REST API 및 세션 인증, PostgreSQL 영속화 (`http://127.0.0.1:5200`)
- **감시 프론트엔드 (`monitor/frontend/`)**: Vite + React 기반 대시보드 UI (`http://127.0.0.1:5173`)
- **데이터베이스**: PostgreSQL (`general_db`, `monitor_db`)

---

## 2. 사용한 시작 자료 및 직접 구현/수정한 내역

- **시작 자료**: 수업 제공 Day4 시작 자료 (`mini-watch/tree/day04-start`)
- **직접 구현 및 수정한 내역**:
  1. **데이터베이스 확장**:
     - `monitor/backend/sql/day04.sql`: `notes` 테이블에 관찰 메모 처리 상태(`status`) 컬럼 추가 (`DEFAULT '확인 전'`).
  2. **감시 백엔드 (`monitor/backend/`)**:
     - `app.py`: `monitor_session` 세션 쿠키 설정 적용.
     - `routes/auth.py`: `POST /api/auth/login`(세션 등록 및 CSRF 발급), `GET /api/auth/me`(세션 복원), `POST /api/auth/logout`(세션 파기) 구현.
     - `note_rules.py`: 제목·내용 공백 검증 및 처리 상태(`"확인 전"`, `"확인 중"`, `"완료"`) 유효성 검사 구현 (400 오류 처리).
     - `repositories/notes.py`: 메모 CRUD 전체에 `status` 컬럼 연동.
     - `routes/notes.py`: 세션 기반 API 접근 보호(`api_access_error`) 적용 및 `status` 필드 처리.
     - `repositories/events.py` & `routes/events.py`: 요청 기록의 `path`(경로 부분 검색) 및 `status_code`(상태 코드 필터) 매개변수 바인딩 쿼리 구현.
  3. **감시 프론트엔드 (`monitor/frontend/`)**:
     - `src/api/client.js`: 세션 쿠키 전송(`credentials: "same-origin"`) 및 자동 `X-CSRF-Token` 헤더 첨부 지원.
     - `src/api/auth.js`, `notes.js`, `events.js`: 확장된 API 스펙(세션 복원, 필터, 상태 변경) 함수 구현.
     - `App.jsx`: 첫 마운트 시 `getMe()`로 세션 유지/복원 및 로그아웃 플로우 완성.
     - `Dashboard.jsx`: 메모 및 이벤트 데이터 바인딩, 실시간 필터 상태 관리, 새로고침 처리.
     - `NoteForm.jsx` / `NoteDetail.jsx` / `NoteList.jsx`: 처리 상태 선택(Select) 및 뱃지/태그 UI 추가.
     - `EventList.jsx`: 전체 요청 건수 및 오류 요청 건수(4xx/5xx) 요약 카드 추가, 경로/상태코드 필터 검색 폼 및 초기화 버튼 구현.

---

## 3. 체크리스트 충족 현황

### 필수 과제 (20/20 충족)
- [x] Flask 백엔드와 React 프론트엔드를 실행하고 API로 연결했다.
- [x] PostgreSQL에 psycopg로 연결하고 SQL에 입력값을 전달할 때 매개변수 바인딩(`%s`)을 사용했다.
- [x] 작성·수정한 자료가 DB에 저장되며 프로그램을 다시 실행해도 유지된다.
- [x] 로그인 입력값을 React state로 관리하고 Flask API로 전송한다.
- [x] Flask에서 DB의 계정과 비밀번호 해시를 확인해 로그인 성공·실패를 판정한다.
- [x] 로그인 성공 시 대시보드를 표시하고 로그아웃 시 로그인 화면으로 돌아간다.
- [x] 일반 서비스에서 수집한 요청 기록의 메서드·경로·상태 코드를 표시한다.
- [x] 관찰 메모 목록을 표시하고 선택한 메모의 상세 내용을 조회한다.
- [x] 새 메모를 작성하면 DB에 저장되고 목록에 반영된다.
- [x] 기존 메모의 내용을 불러와 수정하고 DB와 화면에 반영한다.
- [x] 삭제 확인·취소를 제공하고 확정한 메모만 DB와 화면에서 제거한다.
- [x] 목록 새로고침 버튼으로 최신 메모와 요청 기록을 다시 조회한다.
- [x] 빈 값이나 공백뿐인 작성·수정 요청을 서버에서 400으로 거절하고 기존 자료를 유지한다.
- [x] 존재하지 않는 메모의 조회·수정·삭제 요청에 404를 반환한다.
- [x] 로그인이나 API 요청에 실패하면 화면에 오류 메시지를 표시한다.
- [x] React 화면을 역할별 컴포넌트로 분리하고 필요한 데이터와 함수를 props로 전달한다.
- [x] React의 API 요청 함수를 화면 컴포넌트와 별도 파일로 분리한다.
- [x] Flask의 라우터·DB 처리를 분리하고 app.py에서 연결한다.
- [x] 환경 설정 예시를 제공하고 실제 비밀번호가 담긴 .env는 Git에서 제외한다.
- [x] 패키지 설치 파일과 README를 제공해 DB 준비부터 서버·프론트 실행까지 따라 할 수 있게 한다.

### 선택 심화 과제 (4/4 충족)
- [x] **요청 기록 검색·필터**: 경로 검색과 응답 상태 코드 조건을 지원하며 조건 초기화 시 전체 목록으로 복귀.
- [x] **요청 건수 요약**: 조회된 전체 요청 건수와 오류 요청(4xx/5xx) 건수를 상단 카드로 명시 및 목록 데이터와 일치.
- [x] **메모 처리 상태**: "확인 전", "확인 중", "완료" 상태를 DB에 저장/수정하고 새로고침 후에도 유지.
- [x] **세션 유지와 API 보호**: `monitor_session` 쿠키 기반 세션 유지(새로고침 유지) 및 비로그인 시 보호 대상 API(401) 차단.

---

## 4. 환경 설정 및 실행 가이드 (Windows CMD 기준)

### 4.1 환경 변수 설정 (.env)
`general/.env.example` 및 `monitor/backend/.env.example`을 복사하여 각 디렉터리에 `.env`를 생성합니다.

```cmd
:: general/.env 생성
copy general\.env.example general\.env

:: monitor/backend/.env 생성
copy monitor\backend\.env.example monitor\backend\.env
```

각 `.env` 파일의 `DB_PASSWORD` 및 `SECRET_KEY`를 설정합니다:
```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=monitor_db    # general/.env는 general_db
DB_USER=postgres
DB_PASSWORD=본인_DB_비밀번호
SECRET_KEY=32자_이상의_임의_비밀키
```

### 4.2 DB 스키마 및 실습 계정 준비
1. PostgreSQL(pgAdmin 등)에서 `general_db`에 `general/sql/day04.sql`을 실행합니다.
2. `monitor_db`에 `monitor/backend/sql/day04.sql`을 실행합니다.
3. 실습 계정을 생성합니다:

```cmd
:: 일반 서비스 계정 생성 (student / Learn123!)
cd C:\work\mini-watch-day04\general
..\venv\Scripts\activate
python create_user.py

:: 감시 서비스 계정 생성 (operator / Learn123!)
cd C:\work\mini-watch-day04\monitor\backend
..\..\venv\Scripts\activate
python create_user.py
```

### 4.3 서비스 실행 (각각 별도의 CMD 창에서 실행)

**1) 일반 서비스 실행 (Port: 5100)**
```cmd
cd C:\work\mini-watch-day04\general
..\venv\Scripts\activate
python app.py
```
접속: `http://127.0.0.1:5100`

**2) 감시 Flask API 실행 (Port: 5200)**
```cmd
cd C:\work\mini-watch-day04\monitor\backend
..\..\venv\Scripts\activate
python app.py
```
헬스체크: `http://127.0.0.1:5200/health`

**3) 감시 React 프론트엔드 실행 (Port: 5173)**
```cmd
cd C:\work\mini-watch-day04\monitor\frontend
npm run dev
```
접속: `http://127.0.0.1:5173`

---

## 5. 통합 확인 시나리오 결과

1. **일반 게시판 동작 및 요청 로그 수집**:
   - `http://127.0.0.1:5100/` 접속 및 게시글 열람.
   - 존재하지 않는 주소(`http://127.0.0.1:5100/board/9999`) 접속 시 404 발생.
2. **감시 서비스 로그인 및 세션 유지**:
   - 잘못된 비밀번호 입력 시 401 오류 메시지 확인.
   - `operator` / `Learn123!` 로그인 성공 시 대시보드 진입.
   - 브라우저 새로고침 시 세션이 유지되어 대시보드가 그대로 표시됨.
3. **요청 기록 확인, 요약 통계 및 필터링**:
   - 일반 서비스에서 접속했던 경로(`/board/9999`, 404 등)가 최근 요청 기록 테이블에 표시됨.
   - 상단 요약 카드에 전체 요청 건수 및 404 오류 건수가 정확히 일치하여 집계됨.
   - 경로 검색(`/board`) 및 상태 코드 필터(`404`) 적용 시 조건에 맞는 로그만 필터링됨.
   - 필터 초기화 클릭 시 전체 목록으로 복귀.
4. **관찰 메모 CRUD 및 상태 관리**:
   - 새 메모 작성: "404 요청 확인" / 내용 입력 / 상태 "확인 중" 선택 후 저장 ➔ 목록과 상세에 상태 뱃지와 함께 반영.
   - 메모 수정: 내용 변경 및 상태 "완료"로 변경 저장 ➔ 정상 갱신.
   - 공백 수정 시도: 제목이나 내용을 지우고 저장 시 400 에러 안내 표시 및 기존 자료 보존.
   - 삭제 확인 및 취소: 삭제 버튼 클릭 시 확인 창 노출 ➔ 취소 클릭 시 보존 ➔ 삭제 확인 클릭 시 DB에서 제거.
5. **로그아웃**:
   - 상단 로그아웃 버튼 클릭 시 세션이 해제되고 로그인 폼으로 정상 복귀.
