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

Supabase 대신 **Neon** 서버리스 PostgreSQL을 사용합니다. 일반과 감시는 **별개의 Neon 프로젝트**로 분리합니다.

> **주의**: 두 DB의 `DB_NAME`이 모두 `neondb`여도 **같은 DB가 아닙니다**. 각각 다른 Neon 프로젝트의 엔드포인트를 사용합니다.

### Neon 접속 설정 (Supabase Session pooler 대응 표)

| Supabase 항목 | Neon 대응 항목 |
|---|---|
| Session pooler Host | Neon Endpoint Host (또는 Pooler Host) |
| Session pooler Port (6543) | `5432` |
| DB 이름 `postgres` | Neon 기본 DB `neondb` |
| User (Supabase) | `neondb_owner` (또는 생성한 Role) |
| SSL require | `DB_SSLMODE=require` (동일) |

### 환경 변수 목록

**일반 Flask 필수 환경 변수**

```
DB_HOST=your-neon-project-endpoint.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=...
DB_SSLMODE=require
SECRET_KEY=...              # 32자 이상 무작위 문자열
SESSION_COOKIE_SECURE=true  # Render HTTPS 환경
MONITOR_URL=https://your-monitor-api.onrender.com/api/events
EVENT_TOKEN=...             # 감시 앱과 같은 값
SENTRY_DSN=...              # 선택
SENTRY_ENVIRONMENT=mini-general
APP_VERSION=1.0.0
ENABLE_SENTRY_TEST=false
```

**감시 Flask 필수 환경 변수**

```
DB_HOST=your-neon-monitor-endpoint.neon.tech   # 일반과 다른 엔드포인트
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=...
DB_SSLMODE=require
SECRET_KEY=...              # 일반 앱과 다른 값으로 독립 설정
SESSION_COOKIE_SECURE=true
EVENT_TOKEN=...             # 일반 앱과 같은 값
SENTRY_DSN=...              # 선택
SENTRY_ENVIRONMENT=mini-monitor
APP_VERSION=1.0.0
```

**감시 Next.js 필수 환경 변수**

```
MONITOR_API_URL=https://your-monitor-api.onrender.com   # 서버 전용, NEXT_PUBLIC_ 사용 금지
```

### DB 테이블 준비 (deploy.sql 실행)

Neon 콘솔 SQL Editor 또는 psql로 각 DB에 실행합니다.

**일반 DB** (`general/sql/deploy.sql`):
- `users` (id, username, password_hash)
- `posts` (id, title, body)

**감시 DB** (`monitor/backend/sql/deploy.sql`):
- `users` (id, username, password_hash)
- `http_events` (id, occurred_at, method, path, status_code, event_type)
- `notes` (id, title, body)

### 계정 준비 (create_user.py)

테이블 생성 후, 각 앱의 로컬 가상환경에서 실행합니다.

```bash
# 일반 앱 계정
cd general
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python create_user.py

# 감시 앱 계정
cd monitor/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python create_user.py
```

각 앱의 `.env`에 해당 DB 연결 정보가 설정되어 있어야 합니다.

---

## 4. 네트워크 요청 흐름

```
브라우저
  │
  ▼ (같은 사이트의 /api/... 요청, credentials: same-origin)
Next.js 서버 (Route Handler: app/api/[...path]/route.js)
  │  MONITOR_API_URL을 서버에서 읽어 감시 Flask로 전달
  │  Cookie, X-CSRF-Token → 전달
  │  Set-Cookie, 상태 코드 ← 전달
  ▼
감시 Flask (monitor/backend)
  │  EVENT_TOKEN 검증 (POST /api/events)
  │  세션 쿠키·CSRF 검증 (인증 필요 경로)
  ▼
Neon 감시 DB (users, http_events, notes)

일반 Flask (general)
  │  after_request: record_request()
  │  MONITOR_URL + EVENT_TOKEN 헤더로 POST
  ▼
감시 Flask /api/events (TOKEN 검증 후 DB 저장)
```

### 주소 설정 관계

| 변수 | 설정 위치 | 역할 |
|---|---|---|
| `MONITOR_URL` | 일반 Flask `.env` | 감시 Flask `/api/events` HTTPS 주소 |
| `EVENT_TOKEN` | 일반 Flask `.env` & 감시 Flask `.env` | 동일한 값으로 토큰 검증 |
| `MONITOR_API_URL` | 감시 Next.js `.env` | 브라우저 요청을 전달할 감시 Flask 주소 |

---

## 5. 세션 키 분리와 쿠키 보안 설정

- **일반 앱 세션**: 쿠키 이름 `general_session`, `SECRET_KEY` 독립 설정
- **감시 앱 세션**: 쿠키 이름 `monitor_session`, `SECRET_KEY` 독립 설정
- **로컬 HTTP**: `.env`에 `SESSION_COOKIE_SECURE=false`
- **Render HTTPS**: 환경 변수에 `SESSION_COOKIE_SECURE=true`

---

## 6. Sentry 오류 수정 보고서

### 수정한 파일 및 함수

| 항목 | 내용 |
|---|---|
| 파일 | `general/app.py` |
| 함수 | `sentry_test()` (`/api/sentry-test`) |
| 오류 원인 | 실습용으로 의도적으로 삽입된 `1/0` (`ZeroDivisionError`) |
| 수정 내용 | `1/0` 제거 후 정상 JSON `{"message": "...", "status": "ok"}` 반환 |
| 유지한 조건 | 로그인 확인, `ENABLE_SENTRY_TEST` 플래그, 기존 게시글·로그인 기능 |

### Sentry 실습 절차

1. `.env`에서 `ENABLE_SENTRY_TEST=true`로 변경
2. 로그인 후 `/api/sentry-test` 요청 → Sentry 대시보드에서 이벤트 수신 확인
3. 코드 수정 후 커밋·push·재배포
4. 같은 경로 재요청 → 정상 JSON 응답 확인
5. `.env`에서 `ENABLE_SENTRY_TEST=false`로 되돌림

> **참고**: Sentry의 Resolve 버튼은 대시보드에서 이벤트를 해결 처리하는 것일 뿐, 코드의 오류를 수정하거나 재배포를 대신하지 않습니다.

### Sentry PII(개인 식별 정보) 제외 설정

`observability.py`의 `sentry_sdk.init()`에서 `send_default_pii=False` 설정이 다음을 제외합니다:
- 요청 본문 (request body)
- 쿠키 (cookies)
- 요청 헤더 (request headers)
- 사용자 IP·사용자 정보

---

## 7. 커밋 식별자 및 변경 요약

커밋 완료 후 아래를 채워 넣습니다.

| 커밋 | 식별자 | 변경 파일 | 설명 |
|---|---|---|---|
| 배포 설정 추가 | (커밋 후 기재) | requirements.txt, Dockerfile, db.py, observability.py, auth_helpers.py, request_logging.py, app.py, .env.example, sql/deploy.sql | Neon DB 연동, Waitress 배포, Sentry 연결 |
| Sentry 오류 수정 | (커밋 후 기재) | general/app.py | /api/sentry-test ZeroDivisionError 제거, 정상 JSON 반환 |
| Route Handler 추가 | (커밋 후 기재) | monitor/next-frontend/app/api/[...path]/route.js, .env.example | Next.js 프록시 구현 |

---

## 8. 트러블슈팅 가이드 (심화)

### 설정 오류 진단

| 증상 | 확인할 항목 | 로그 위치 |
|---|---|---|
| 감시 Flask `/health` 200 → DB 작업 실패 | `DB_HOST`, `DB_PORT`, `DB_SSLMODE` 환경 변수 | Render 로그 > `OperationalError` |
| 일반 Flask → 감시 Flask 전송 실패 | `MONITOR_URL` 주소, `EVENT_TOKEN` 값 | Render 로그 > "감시 서비스에 요청 기록을 보내지 못했습니다" |
| Next.js → 감시 Flask 502 | `MONITOR_API_URL` 주소 오타, 감시 Flask 미실행 | Next.js 서버 로그 > "[proxy] 감시 Flask 연결 실패" |
| 로그인 후 세션 유지 안됨 | `SESSION_COOKIE_SECURE` 설정, `SECRET_KEY` 일치 여부 | 브라우저 DevTools > Application > Cookies |

### `/health` 성공 ≠ DB 연결 성공

`/health`는 DB 없이도 `{"status": "ok"}`를 반환합니다. DB 연결 성공은 실제 로그인·게시글 조회·메모 등록으로 확인해야 합니다.

### Next 프록시 연결 실패 응답

`route.js`는 다음 상황에서 오류 응답을 반환합니다:
- `MONITOR_API_URL` 미설정: `503` + `"감시 API 주소가 설정되지 않았습니다."`
- 감시 Flask 연결 실패: `502` + `"감시 서비스에 연결할 수 없습니다."` (화면에서 재시도 가능)
