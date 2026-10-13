# Deployment Plan

## 1. 배포 저장소 및 브랜치

| 항목 | 값 |
|---|---|
| 저장소 | 본인 GitHub 저장소 |
| 배포 브랜치 | `day2-deploy` |

---

## 2. 세 앱의 Render 배포 설정

Render > New > Web Service > Deploy an existing image from a registry가 아닌 **Build and deploy from a Git repository** 방식으로 세 앱 각각을 Docker Web Service로 배포합니다.

| 앱 | Root Directory | Dockerfile Path | Health Check Path | Docker Build Context | Docker Command | Auto-Deploy |
|---|---|---|---|---|---|---|
| 일반 앱 (general) | `general` | `./Dockerfile` | `/health` | `.` | (빈칸) | On Commit |
| 감시 API (monitor/backend) | `monitor/backend` | `./Dockerfile` | `/health` | `.` | (빈칸) | On Commit |
| 감시 화면 (monitor/next-frontend) | `monitor/next-frontend` | `./Dockerfile` | `/` | `.` | (빈칸) | On Commit |

### 배포 현황

| 앱 | 상태 | 배포 주소 |
|---|---|---|
| 일반 앱 | 설정 완료 (미배포) | 미배포 |
| 감시 API | 설정 완료 (미배포) | 미배포 |
| 감시 화면 | 설정 완료 (미배포) | 미배포 |

### Flask Waitress 실행

두 Flask 앱은 Dockerfile에서 Waitress로 실행합니다.

```
CMD ["sh", "-c", "exec waitress-serve --port=${PORT:-5000} --host=0.0.0.0 app:app"]
```

- `${PORT:-5000}`: Render가 주입하는 `PORT` 환경 변수를 우선 사용. 없으면 5000 사용.
- 로컬 개발: `python app.py` (변경 없음)
- Waitress 실행에서도 `app.py` 최상단의 `init_observability()` 가 실행되어 Sentry가 활성화됩니다.

### Next.js 빌드 안전성

```dockerfile
RUN npm ci           # package-lock.json 기반 설치 (재현 가능한 의존성)
RUN npm run build    # 빌드 중 외부 API·DB 응답을 요구하지 않음
CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0"]
```

- API 데이터는 실제 요청이 올 때 Route Handler에서 읽습니다. 빌드 시점에 외부 서버가 없어도 됩니다.

### 두 Compose 파일의 역할

`compose-general.yaml`, `compose-monitor.yaml`은 **로컬 개발·실습 전용**입니다. Render 배포는 각 앱의 Dockerfile을 독립적으로 빌드하므로 Compose를 사용하지 않습니다.

---

## 3. Neon DB 구성 (일반·감시 DB 분리)

본 프로젝트는 Supabase 대신 서버리스 PostgreSQL 플랫폼인 **Neon (neon.tech)** 을 데이터베이스 서버로 채택하여 전면 재구성했습니다. 일반 앱과 감시 앱은 데이터 격리를 위해 **서로 다른 독립된 Neon 프로젝트**(또는 독립 브랜치)의 엔드포인트를 사용합니다.

> **주의**: 두 DB의 데이터베이스 이름(`DB_NAME`)이 기본값인 `neondb`로 같더라도, 호스트 엔드포인트(`DB_HOST`)가 다르므로 **완전히 물리적으로 분리된 별개의 독립 DB**입니다.

### Neon 연결 아키텍처 및 Supabase 비교

| 항목 | Supabase (기존 수업 기준) | Neon (본 프로젝트 적용) | 비고 |
|---|---|---|---|
| **서비스 종류** | Supabase PostgreSQL | **Neon Serverless PostgreSQL** | 서버리스 풀 매니지드 DB |
| **연결 방식** | Session pooler (IPv4 호환) | **Neon Connection Pooler** (pgBouncer 내장) | 서버리스 환경에 최적화 |
| **호스트 (Host)** | `aws-0-...pooler.supabase.com` | `ep-xxxx-pooler.region.neon.tech` (또는 direct) | 각 프로젝트별 고유 엔드포인트 |
| **포트 (Port)** | `5432` (또는 6543) | **`5432`** | 표준 PostgreSQL 포트 |
| **DB 이름** | `postgres` | **`neondb`** (또는 사용자 지정 DB) | Neon 기본 생성 DB명 |
| **기본 사용자** | `postgres` | **`neondb_owner`** (또는 생성한 Role) | Neon 기본 관리자 Role |
| **SSL 모드** | `require` | **`DB_SSLMODE=require`** | Neon은 SSL 암호화 연결 필수 |

- **Connection Pooling**: Neon은 엔드포인트 호스트명에 `-pooler` 접미사가 포함된 풀러 호스트를 제공합니다. 다수의 클라이언트나 서버리스 컨테이너 환경에서 커넥션 고갈 없이 안정적으로 작동합니다.
- **SSL 필수**: Neon은 모든 외부 연결에 대해 TLS/SSL 암호화를 강제하므로, `db.py`에서 `DB_SSLMODE=require`를 전달합니다.

### 환경 변수 목록

**일반 Flask 필수 환경 변수 (`general/.env`)**

```ini
# Neon 일반 DB 연결 설정 (일반 프로젝트 전용 엔드포인트)
DB_HOST=ep-your-general-pooler.us-east-2.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=YOUR_NEON_GENERAL_PASSWORD
DB_SSLMODE=require

# 세션 암호화 키 (32자 이상 무작위 문자열)
SECRET_KEY=CHANGE_ME_TO_YOUR_OWN_RANDOM_SECRET_KEY_32CHARS
SESSION_COOKIE_SECURE=true  # Render HTTPS 환경 (로컬 개발 시 false)

# 감시 Flask 주소 및 토큰
MONITOR_URL=https://your-monitor-api.onrender.com/api/events
EVENT_TOKEN=YOUR_SHARED_EVENT_TOKEN_HERE

# Sentry 오류 수집
SENTRY_DSN=
SENTRY_ENVIRONMENT=mini-general
APP_VERSION=1.0.0
ENABLE_SENTRY_TEST=false
```

**감시 Flask 필수 환경 변수 (`monitor/backend/.env`)**

```ini
# Neon 감시 DB 연결 설정 (일반 DB와 다른 별개 프로젝트 엔드포인트)
DB_HOST=ep-your-monitor-pooler.us-east-2.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=YOUR_NEON_MONITOR_PASSWORD
DB_SSLMODE=require

# 세션 암호화 키 (일반 앱과 다른 값으로 독립 설정)
SECRET_KEY=ANOTHER_RANDOM_SECRET_KEY_FOR_MONITOR_32CHARS
SESSION_COOKIE_SECURE=true  # Render HTTPS 환경 (로컬 개발 시 false)

# 일반↔감시 요청 검증 토큰 (일반 앱의 EVENT_TOKEN과 동일값)
EVENT_TOKEN=YOUR_SHARED_EVENT_TOKEN_HERE

# Sentry 오류 수집
SENTRY_DSN=
SENTRY_ENVIRONMENT=mini-monitor
APP_VERSION=1.0.0
```

**감시 Next.js 필수 환경 변수 (`monitor/next-frontend/.env`)**

```ini
# 감시 Flask 주소 (서버 Route Handler 전용 — 절대 NEXT_PUBLIC_ 접두사 사용 금지)
MONITOR_API_URL=https://your-monitor-api.onrender.com
```

### DB 테이블 준비 (배포 DDL 실행)

Neon 콘솔(https://console.neon.tech)의 **SQL Editor** 또는 로컬 `psql` 클라이언트를 사용하여 각 DB에 스키마를 생성합니다.
모든 DDL은 `CREATE TABLE IF NOT EXISTS`를 사용하여 기존 테이블이나 저장 데이터를 삭제/초기화하지 않습니다.

1. **일반 DB 스키마 (`general/sql/deploy.sql`)**:
   ```sql
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
   ```

2. **감시 DB 스키마 (`monitor/backend/sql/deploy.sql`)**:
   ```sql
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
       event_type TEXT NOT NULL
   );

   CREATE TABLE IF NOT EXISTS notes (
       id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       title TEXT NOT NULL,
       body TEXT NOT NULL
   );
   ```

### 계정 준비 (`create_user.py`)

각 앱의 DB 테이블 생성 후, 로컬 가상환경에서 `create_user.py`를 실행하여 초기 관리 계정을 준비합니다.
비밀번호는 평문이 아닌 `werkzeug.security.generate_password_hash`를 통한 안전한 해시값으로 DB에 저장됩니다.

```bash
# 1. 일반 앱 계정 생성 (student 계정)
cd general
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows CMD: .venv\Scripts\activate.bat
pip install -r requirements.txt
python create_user.py

# 2. 감시 앱 계정 생성 (operator 계정)
cd ../monitor/backend
python -m venv .venv
# 가상환경 활성화
pip install -r requirements.txt
python create_user.py
```

---

## 4. 네트워크 요청 흐름

```
[사용자 브라우저]
  │
  ▼ 1. 브라우저는 같은 출처의 상대 경로(/api/...)로 요청 (credentials: same-origin)
[Next.js 서버 Route Handler] (app/api/[...path]/route.js)
  │  - 서버 전용 환경 변수 MONITOR_API_URL을 읽어 감시 Flask로 전달
  │  - 요청의 Cookie, X-CSRF-Token, Content-Type 전달
  │  - 감시 Flask의 Set-Cookie, Content-Type, HTTP 상태 코드 전달
  ▼ 2. 백엔드 통신
[감시 Flask] (monitor/backend)
  │  - POST /api/events: X-Event-Token 헤더 검증 (비밀 토큰)
  │  - 인증 필요 API: 세션 쿠키(monitor_session) 및 X-CSRF-Token 검증
  ▼ 3. DB 질의
[Neon 감시 DB] (users, http_events, notes 영구 보관)

[일반 Flask] (general)
  │  - 사용자 요청 처리 후 after_request 훅에서 record_request() 실행
  │  - MONITOR_URL + X-Event-Token 헤더로 POST /api/events 전송
  ▼
[감시 Flask]
  │  - 토큰 일치 확인 후 make_event()로 이벤트 분류
  │  - 일반 로그인 실패(/auth/login 401) -> login_failure
  │  - 일반 로그인 성공(/auth/login 200) -> login_success
  │  - 기타 일반 요청 -> http_request
  ▼
[Neon 감시 DB]
```

### 주소 설정 관계

| 환경 변수 | 설정 위치 | 값 설명 | 브라우저 노출 여부 |
|---|---|---|---|
| `MONITOR_URL` | 일반 Flask `.env` | 감시 Flask의 HTTPS 주소 + `/api/events` | **노출 안 됨** (서버 간 전송) |
| `EVENT_TOKEN` | 일반 & 감시 Flask `.env` | 두 서버 간 요청을 인증하는 동일한 비밀 토큰 | **노출 안 됨** (백엔드 전용) |
| `MONITOR_API_URL` | 감시 Next.js `.env` | 감시 Flask의 기본 HTTPS 주소 | **노출 안 됨** (서버 Route Handler 전용) |

---

## 5. 세션 키 분리와 쿠키 보안 설정

- **일반 Flask**:
  - 세션 쿠키 이름: `general_session`
  - `SECRET_KEY`: 일반 앱 전용 32자 이상 무작위 문자열
  - `SESSION_COOKIE_SECURE`: 로컬 HTTP 환경 `false`, Render HTTPS 환경 `true`
- **감시 Flask**:
  - 세션 쿠키 이름: `monitor_session`
  - `SECRET_KEY`: 감시 앱 전용 독립 32자 이상 무작위 문자열 (일반 앱과 분리)
  - `SESSION_COOKIE_SECURE`: 로컬 HTTP 환경 `false`, Render HTTPS 환경 `true`
- **쿠키 격리**:
  - 서로 다른 쿠키 이름과 서명 키를 사용하여 두 서비스 간의 세션 탈취 및 충돌을 원천 방지합니다.

---

## 6. Sentry 오류 수정 보고서

### 수정한 파일 및 함수

| 항목 | 내용 |
|---|---|
| 파일 | `general/app.py` |
| 함수 | `sentry_test()` (`/api/sentry-test`) |
| 오류 원인 | 실습을 위해 의도적으로 작성된 `1 / 0` (`ZeroDivisionError: division by zero`) |
| 수정 내용 | `1 / 0` 제거 후 정상 응답 `{"message": "sentry-test 요청을 정상적으로 처리했습니다.", "status": "ok"}` 반환 |
| 유지한 조건 | `current_user()` 로그인 검증(401), `ENABLE_SENTRY_TEST` 플래그 체크, 기존 게시글/로그인 기능 보존 |

### 오류 수정 코드 Diff 비교 (심화)

```diff
--- a/general/app.py
+++ b/general/app.py
@@ -36,8 +36,9 @@ def sentry_test():
     if os.environ.get("ENABLE_SENTRY_TEST", "false").lower() != "true":
         return {"message": "sentry-test가 비활성화되어 있습니다. ENABLE_SENTRY_TEST=true로 설정하면 활성화됩니다."}
-    # 의도적인 0으로 나누기 오류
-    return 1 / 0
+    # 의도적인 오류 제거: 기존 1/0 오류를 정상 JSON 반환으로 수정
+    # 수정 전: return 1 / 0  (ZeroDivisionError 발생)
+    # 수정 후: 정상 JSON 반환
+    return {"message": "sentry-test 요청을 정상적으로 처리했습니다.", "status": "ok"}
```

- **수정 이유**: 서비스 안정성을 위해 비정상적인 서버 크래시를 제거하고 클라이언트가 성공 상태를 인지할 수 있는 표준 JSON 응답을 반환하도록 수정했습니다.
- **기존 조건 유지 이유**: 관리자만 테스트할 수 있도록 로그인 검증을 유지하고, 상용 환경에서 의도치 않은 테스트 경로 노출을 막기 위해 `ENABLE_SENTRY_TEST` 환경 변수 제어 기능을 보존했습니다.

### Sentry 실습 절차 및 재배포 흐름

1. `.env`에서 `ENABLE_SENTRY_TEST=true`로 임시 설정
2. 브라우저에서 로그인 후 `/api/sentry-test` 접속 → Sentry 대시보드에서 `ZeroDivisionError` 이벤트 수신 확인
3. `general/app.py` 코드 수정 (정상 JSON 반환)
4. Git 커밋 & push → Render Auto-Deploy로 새 버전 배포
5. 배포 완료 후 같은 경로 재요청 → 200 OK 및 정상 JSON 응답 확인
6. 확인 완료 후 `.env`에서 `ENABLE_SENTRY_TEST=false`로 되돌림

> **주의**: Sentry 대시보드의 **Resolve** 버튼은 단순 관리용 상태 플래그 변경일 뿐입니다. 실제 소스 코드 수정과 Git 커밋·재배포를 대신하지 않습니다.

### Sentry PII(개인 식별 정보) 제외 설정 (심화)

`observability.py`의 `sentry_sdk.init()` 설정 중 `send_default_pii=False`의 역할:
- **제외 대상**: 클라이언트 요청 본문(request body), 쿠키(cookies), 인증 헤더(Authorization, X-CSRF-Token), 클라이언트 IP 주소, 사용자 개인 식별 정보
- **보안 목적**: DB 비밀번호, 세션 토큰, 사용자 비밀번호 등 민감한 데이터가 외부 모니터링 SaaS 플랫폼으로 유출되는 보안 사고를 원천 방지합니다.

---

## 7. 커밋 식별자 및 변경 요약

| 커밋 식별자 | 변경 파일 목록 | 설명 |
|---|---|---|
| `484f404` | `general/*`, `monitor/backend/*`, `monitor/next-frontend/*`, `deployment-plan.md`, `README.md` | Neon DB 연동, Waitress WSGI 배포 구성, Sentry 연동 및 실습 오류 수정, Route Handler 프록시 구현 |
| `982e8d5` | `deployment-plan.md` | 커밋 해시 기록 및 배포 계획 문서 정리 |
| `최신` | `general/app.py`, `monitor/backend/app.py`, `deployment-plan.md`, `README.md` | 앱 시작 시 명시적 load_dotenv 로드 보완 및 Neon DB 아키텍처/심화 가이드 상세 재구성 |

---

## 8. 트러블슈팅 가이드 (심화)

### 설정 오류 진단 경로 및 우선 확인 로그

| 증상 | 발생 원인 | 우선 확인할 설정 및 로그 |
|---|---|---|
| **감시 Flask `/health` 200인데 기능 실패** | DB 접속 실패 (`DB_HOST`, `DB_PORT`, `DB_SSLMODE` 등) | Render 로그 > `psycopg.OperationalError` 확인. `/health`는 DB 쿼리를 수행하지 않으므로 DB 정상 여부를 보장하지 않음. |
| **일반 Flask → 감시 Flask 전송 실패** | `MONITOR_URL` 오타 또는 `EVENT_TOKEN` 불일치 | 일반 Flask Render 로그 > `"감시 서비스에 요청 기록을 보내지 못했습니다."` 및 감시 Flask 로그의 `401 Unauthorized`. |
| **Next.js → 감시 Flask 502 / 503** | `MONITOR_API_URL` 미설정(503) 또는 감시 Flask 다운/주소 오타(502) | Next.js 서버 콘솔 로그 > `"[proxy] 감시 Flask 연결 실패"`. |
| **로그인 후 세션 유실 (무한 로그인 루프)** | `SESSION_COOKIE_SECURE=true`인데 HTTP 접속 시 쿠키 거부, 또는 `SECRET_KEY`가 변경됨 | 브라우저 개발자 도구(F12) > Application > Cookies에 세션 쿠키 저장 여부 확인. |

### `/health` 성공과 실제 DB 작업 성공의 명확한 차이

- `/health`는 웹 서버 프로세스가 살아있는지 확인하는 **Liveness Probe** 역할만 수행하며, 외부 DB 연결 상태를 질의하지 않습니다.
- 따라서 `/health` 응답이 200이라 하더라도 DB 인증 실패, 네트워크 단절, 테이블 미존재 등의 오류가 있을 수 있으므로 반드시 로그인·게시글 등록·메모 생성 등의 실제 트랜잭션으로 기능을 검증해야 합니다.

### Next.js Route Handler의 실패 처리 및 프론트엔드 연동

1. **503 Service Unavailable**:
   - 상황: Next.js 서버에 `MONITOR_API_URL` 환경 변수가 누락되었을 때
   - 응답: `{"error": "감시 API 주소(MONITOR_API_URL)가 설정되지 않았습니다."}`
2. **502 Bad Gateway**:
   - 상황: 감시 Flask 서버가 실행 중이지 않거나 네트워크 연결이 끊겼을 때
   - 응답: `{"error": "감시 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요."}`
3. **프론트엔드 화면 처리**:
   - `client.js`가 에러를 catch하여 화면에 경고 배너로 표시하며, 사용자가 화면 새로고침 또는 재시도 버튼을 눌러 다시 호출할 수 있도록 상태를 보존합니다.
