# Mini Watch Day 06

Day06 시작 코드의 `general` 게시물 서비스와 `monitor` 감시 서비스를 Docker Compose 두 개로 실행합니다. 이번 적용에서 직접 완성한 Docker 설정은 `compose-general.yaml`, `compose-monitor.yaml`, 두 Flask Dockerfile, 일반 서비스 초기 SQL과 gateway, 감시 DB 초기 SQL입니다. 기존 Flask·React/Next.js 앱 코드는 유지했습니다.

## 구성

| Compose 프로젝트 | 서비스 | 역할 | PC 공개 포트 |
| --- | --- | --- | --- |
| `m5d1-general` | `general-db`, `general-api`, `general-gateway` | 게시물·로그인 서비스 | gateway만 `127.0.0.1:8081:80` |
| `m5d1-monitor` | `monitor-db`, `monitor-api`, `monitor-web`, `monitor-gateway` | 요청 기록·메모 화면 | gateway만 `127.0.0.1:8082:80` |

각 API는 자기 프로젝트의 DB 전용 망과 gateway/web 망에 연결됩니다. 두 API만 외부 공유 망 `m5d1-events`에 추가로 연결되어 이벤트를 주고받습니다. DB는 공유 망에 들어가지 않습니다. API는 DB 호스트로 자기 DB의 서비스 이름과 내부 포트 `5432`를 사용하며, 일반 API의 감시 주소는 `http://monitor-api:5000/api/events`입니다. Compose 파일마다 `events-net` 같은 논리 이름을 쓸 수 있지만 `external: true`와 `name: m5d1-events`를 함께 지정해야 두 프로젝트가 동일한 실제 네트워크에 참여합니다.

`general/Dockerfile`과 `monitor/backend/Dockerfile`은 Flask 앱을 컨테이너 안에서 `0.0.0.0:5000`으로 실행합니다. `monitor/next-frontend/Dockerfile`은 이미지 빌드 중 `npm run build`를 실행하고 production 서버를 시작합니다. 각 빌드 폴더의 `.dockerignore`는 가상환경, Node 생성물, `.env`와 캐시를 빌드 컨텍스트에서 제외합니다.

## 처음 실행

PowerShell 또는 CMD에서 프로젝트 루트로 이동합니다.

```powershell
docker network create m5d1-events
docker compose -f compose-monitor.yaml config --quiet
docker compose -f compose-general.yaml config --quiet
docker compose -f compose-monitor.yaml up -d --build
docker compose -f compose-monitor.yaml ps
```

감시 API가 준비되면 `http://localhost:8082/api/auth/me`에서 HTTP 200을 확인한 후 일반 서비스를 시작합니다.

```powershell
Invoke-WebRequest http://localhost:8082/api/auth/me -UseBasicParsing
docker compose -f compose-general.yaml up -d --build
docker compose -f compose-general.yaml ps
docker compose -f compose-general.yaml exec general-api python create_user.py
docker compose -f compose-monitor.yaml exec monitor-api python create_user.py
```

실습 계정은 일반 서비스 `student / Learn123!`, 감시 서비스 `operator / Learn123!`입니다. 기존 계정이 있으면 생성 스크립트는 덮어쓰지 않습니다.

## 동작 확인

1. 일반 서비스 [http://localhost:8081](http://localhost:8081)에서 `student`로 로그인해 게시물 화면을 엽니다. 잘못된 비밀번호 로그인도 한 번 시도합니다.
2. 감시 서비스 [http://localhost:8082](http://localhost:8082)에 `operator`로 로그인해 요청 기록을 확인합니다. 이번 로그인 실패는 `login_failure`와 `401`, 성공은 `login_success`와 `200`으로 표시되어야 합니다.
3. 감시 메모에 제목 `Docker 점검`, 내용 `로그인 실패와 성공을 확인했다`를 저장하고 새로고침 후 다시 불러옵니다.
4. 공유 네트워크 참여와 이름 해석을 확인합니다.

```powershell
docker network inspect m5d1-events
docker compose -f compose-general.yaml exec general-api getent hosts monitor-api
docker compose -f compose-general.yaml logs general-api
docker compose -f compose-monitor.yaml logs monitor-api
```

이름 조회는 DNS와 네트워크 연결만 확인합니다. 앱의 이벤트 수신은 감시 화면에서 해당 로그를 확인해야 검증됩니다. `docker compose ... ps`로 DB/API/web/gateway 상태를 확인합니다.

## 재시작과 데이터 보존

두 Compose는 각각 종료하고 다시 실행합니다. `-v`를 붙이지 않아 named volume의 DB 자료를 보존합니다.

```powershell
docker compose -f compose-general.yaml down
docker compose -f compose-monitor.yaml down
docker compose -f compose-monitor.yaml up -d
docker compose -f compose-general.yaml up -d
```

다시 로그인한 뒤 기존 이벤트 기록과 메모가 남아 있는지 확인합니다. 네트워크는 별도 외부 네트워크라 프로젝트 종료 후에도 남으며, 이 실습에서는 삭제하지 않습니다.

## 설정 및 실행 확인 기록

2026-10-12 실제 실행 결과:

- 두 Compose의 `config --quiet`가 오류 없이 종료했습니다. 감시 이미지는 `npm run build`를 포함해 빌드됐고, 일반·감시 컨테이너가 모두 실행 중이며 DB 두 개 모두 `healthy`였습니다.
- 감시 API `http://localhost:8082/api/auth/me`와 일반 홈 `http://localhost:8081/`은 각각 HTTP 200을 반환했습니다. `ps`에서 PC 공개 포트는 gateway의 `127.0.0.1:8081`과 `127.0.0.1:8082`만 확인했습니다.
- `docker network inspect m5d1-events`에 API 컨테이너 2개가 표시됐고 DB 컨테이너는 없었습니다. 일반 API 안의 `getent hosts monitor-api`는 `172.20.0.2 monitor-api`를 반환했습니다. 이는 이름 해석 확인이며, 이벤트 전달은 다음 항목으로 따로 확인했습니다.
- 일반 gateway를 통해 로그인 실패 HTTP 401, 성공 HTTP 200 및 게시물 홈 HTTP 200을 확인했습니다. 감시 화면의 기록 표에 `login_failure /api/auth/login 401`, `login_success /api/auth/login 200`이 표시됐고 감시 DB에도 각 1건 저장됐습니다.
- 감시 화면에서 새 메모 `Docker 점검`을 저장하고 목록을 불러왔으며, 페이지 새로고침 후 다시 로그인해 기록과 메모를 재조회했습니다. 두 Compose를 각각 `down`한 뒤 `-v` 없이 감시→일반 순으로 올린 뒤에도 로그인 이벤트 2건과 메모가 남아 있었습니다.

위 결과는 이 작업 환경에서 직접 실행해 확인했습니다. 다른 PC에서는 실행 환경이 달라질 수 있으므로 같은 절차로 다시 검증해야 합니다.

## Git 제출

Docker 적용 변경 커밋: 아래의 `Docker 적용` 커밋 ID를 확인합니다. README 검증 결과 업데이트는 후속 커밋으로 기록합니다. GitHub 제출 시 해당 커밋을 본인 저장소에 push합니다.

제출물에는 앱 소스, 두 Compose 파일, Dockerfile·`.dockerignore`, 의존성 파일과 잠금 파일, DB 초기 SQL, gateway 설정, README를 포함합니다. `.env`, 실제 비밀값, DB 데이터, `.next`, `node_modules`, 캐시, 가상환경은 제출하지 않습니다. 실습용 환경값 외의 서비스 비밀번호·토큰은 포함하지 않습니다.
