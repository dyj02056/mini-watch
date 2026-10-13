# mini-watch-day06

Flask 기반 일반 앱과 감시 앱, 감시 Next.js 프론트엔드로 구성된 미니프로젝트입니다.  
배포 설정과 Neon DB 연동 등 Day2 작업 내용은 [`deployment-plan.md`](./deployment-plan.md)에 정리했습니다.

---

## 앱 구성

| 앱 | 위치 | 역할 |
|---|---|---|
| 일반 Flask | `general/` | 사용자 로그인·게시글 CRUD, 감시 Flask로 요청 기록 전송 |
| 감시 Flask | `monitor/backend/` | 요청 이벤트 수집·분류·저장, 감시 메모 CRUD |
| 감시 Next.js | `monitor/next-frontend/` | 감시 화면 (로그인·이벤트 조회·메모 관리) |

---

## Day2 직접 변경한 파일과 변경 목적

| 파일 | 변경 목적 |
|---|---|
| `general/requirements.txt` | `waitress`, `sentry-sdk[flask]` 추가 (배포용 WSGI·오류 수집) |
| `general/Dockerfile` | `python app.py` → Waitress + `$PORT` 바인딩 배포 구성 |
| `general/db.py` | `DB_SSLMODE` 환경 변수 지원 추가 (Neon SSL 필수) |
| `general/observability.py` | Sentry 초기화 모듈 신규 생성 (`mini-general` 환경) |
| `general/auth_helpers.py` | `SESSION_COOKIE_SECURE` 환경 변수에서 읽도록 변경 |
| `general/request_logging.py` | `EVENT_TOKEN` 헤더 추가 (감시 Flask 토큰 검증용) |
| `general/app.py` | Sentry 초기화, `/health`, `/api/sentry-test` 오류 수정 추가 |
| `general/.env.example` | Neon DB 환경 변수, MONITOR_URL, EVENT_TOKEN, Sentry 항목 추가 |
| `general/sql/deploy.sql` | `IF NOT EXISTS` 안전 DDL 신규 생성 |
| `monitor/backend/requirements.txt` | `waitress`, `sentry-sdk[flask]` 추가 |
| `monitor/backend/Dockerfile` | Waitress + `$PORT` 배포 구성 |
| `monitor/backend/db.py` | `DB_SSLMODE` 환경 변수 지원 추가 |
| `monitor/backend/observability.py` | Sentry 초기화 모듈 신규 생성 (`mini-monitor` 환경) |
| `monitor/backend/auth_helpers.py` | `SESSION_COOKIE_SECURE` 환경 변수화 |
| `monitor/backend/routes/events.py` | `EVENT_TOKEN` 검증 로직 추가 (`POST /api/events`) |
| `monitor/backend/app.py` | Sentry 초기화 호출 추가 |
| `monitor/backend/.env.example` | Neon DB, EVENT_TOKEN, Sentry 항목 추가 |
| `monitor/backend/sql/deploy.sql` | `IF NOT EXISTS` 안전 DDL 신규 생성 |
| `monitor/next-frontend/app/api/[...path]/route.js` | Route Handler 프록시 신규 생성 |
| `monitor/next-frontend/.env.example` | `MONITOR_API_URL` 항목 신규 생성 |
| `deployment-plan.md` | 전체 배포·연동·오류 수정 문서 |

---

## 시작 코드

Day1 완성 프로젝트(`main` 브랜치)를 기반으로 `day2-deploy` 브랜치에서 작업했습니다.

---

## 로컬 실행 (Compose)

```bash
# 일반 앱 로컬 실행
docker compose -f compose-general.yaml up

# 감시 앱 로컬 실행
docker compose -f compose-monitor.yaml up
```

두 Compose 파일은 로컬 개발 전용입니다. Render 배포는 각 앱의 Dockerfile을 독립적으로 사용합니다.

---

## 계정 준비

```bash
# 일반 앱 계정 생성
cd general && python create_user.py

# 감시 앱 계정 생성
cd monitor/backend && python create_user.py
```

각 앱의 `.env`에 해당 Neon DB 연결 정보 설정 필요. 자세한 내용은 [deployment-plan.md](./deployment-plan.md) 참고.

---

## 배포 현황

자세한 배포 설정과 상태는 [`deployment-plan.md`](./deployment-plan.md)를 참고하세요.
