# mini-watch-day06

일반 게시판에서 발생한 HTTP 요청을 감시 DB에 저장하고, 실제 저장 행으로 목록 조회 횟수와 뒤따른 404 문맥을 계산하는 프로젝트입니다. PCAP·IOC 실습 자료는 HTTP 분석 근거에 포함하지 않습니다.

## 구성과 기록 흐름

| 위치 | 역할 |
|---|---|
| `general/app.py` | `app.after_request(record_request)`로 응답 후 기록 함수를 연결합니다. |
| `general/request_logging.py` | `record_request`가 method·path·status_code를 만들고 표준 출력에 출력한 뒤 `MONITOR_URL`로 POST합니다. 출력과 DB 저장은 별도 동작입니다. |
| `monitor/backend/routes/events.py` | `/api/events`에서 `EVENT_TOKEN`을 확인하고 요청을 검증합니다. |
| `monitor/backend/event_rules.py` | `make_event`가 GET `/` 200을 `post_list`, 404를 `request_error`로 분류합니다. |
| `monitor/backend/repositories/events.py` | `create_event`가 `http_events`에 저장합니다. ID와 `occurred_at`은 DB 기본값으로 붙고, `occurred_at`은 감시 DB의 수신·저장 시각입니다. |
| `monitor/backend/learning/` | 실요청 캡처, 원본 정규화, 조회 행 선택, 뒤따른 오류 선택 및 보고서를 제공합니다. |
| `monitor/backend/routes/analysis.py` | 로그인된 사용자의 관찰 시작과 DB 기반 분석 API입니다. |
| `monitor/next-frontend/components/MonitorClient.js` | 새 관찰·기준 입력·결과 조회 및 근거 행 표시를 제공합니다. |

Compose의 일반 API는 `MONITOR_URL`로 감시 API 주소를 사용하고, 두 API의 `EVENT_TOKEN`이 같을 때 발신자 검증이 통과합니다. Compose 파일의 토큰·세션 키는 로컬 학습용 예시이며 운영에 안전한 비밀값이 아닙니다. 실제 `.env`, 비밀번호, 토큰, 키는 제출하지 마세요.

로컬 Compose의 두 API는 `DB_SSLMODE=disable`로 같은 Compose 네트워크의 PostgreSQL에 연결합니다. Neon 등 TLS를 요구하는 원격 DB 설정에서는 해당 환경에 맞는 SSL 모드를 유지합니다.

분석에서 `http-숫자`는 감시 DB의 원본 ID를 가리킵니다. `http_live` 기록은 실제 HTTP 수신 자료이며 사용자나 IP는 추정하지 않습니다. 조회 횟수는 GET `/` 200 `post_list` 행만 셉니다. 마지막 조회 이후 30초 이내의 404는 별도 문맥 근거로 추가하며 횟수에는 포함하지 않습니다. 검토 후보는 기준 충족을 뜻하며 공격이나 침해 확정이 아니고, 기준 미해당도 정상의 증거가 아닙니다.

## 변경 사항

이번 과제용 추가·수정 파일은 다음과 같습니다.

- 추가: `monitor/backend/routes/analysis.py`, `monitor/backend/learning/{capture_case,normalize,http_rules,report,support,lesson2,lesson3}.py`
- 심화 실습 추가: `monitor/backend/learning/lesson_pcap.py` (표준 라이브러리로 합성 PCAP 생성·읽기), `monitor/backend/learning/lesson_ioc.py` (문서용 IP 문자열 IOC 비교)
- 수정: `general`의 응답 후 이벤트 전송 흐름(기존 유지), `monitor/backend/event_rules.py`, `routes/events.py`, `repositories/events.py`, `app.py`, `requirements.txt`, `compose-general.yaml`, `compose-monitor.yaml`, `monitor/next-frontend/components/MonitorClient.js`, 이 README

기존 앱, DB 볼륨, 계정 및 저장된 행은 유지합니다. 분석의 새 관찰은 현재 마지막 ID를 경계로 삼으며 이전 행을 삭제하지 않습니다.

## 실행 전 준비

Windows CMD에서 기존 프로젝트 루트에서 진행합니다. Docker Desktop과 기존 Compose 프로젝트/외부 `m5d1-events` 네트워크, 일반·감시 DB 및 로그인 계정이 준비되어 있어야 합니다. 기존 폴더나 데이터 볼륨을 지우거나 새로 복제하지 마세요.

아래 캡처 명령은 CMD 문법입니다. PowerShell을 사용한다면 `&&`, `move /Y` 대신 각 단계의 성공을 확인하고 `Move-Item -Force`를 사용하세요. 이 프로젝트의 파일 분석 스크립트는 Windows PowerShell이 저장하는 UTF-8 BOM도 읽습니다.

```bat
docker compose -f compose-general.yaml up -d --build
docker compose -f compose-monitor.yaml up -d --build
```

감시 화면은 `http://localhost:8082`, 일반 게시판은 `http://localhost:8081`입니다. 로그인한 뒤 API 계정이 준비되어 있는지 확인하세요. 일반 서비스는 감시 API가 실행 중일 때 요청을 기록합니다.

## 파일 실습: 실제 4회 사례

캡처 스크립트가 일반 서비스에 실제 GET `/` 요청 4회와 GET `/training-missing` 요청 1회를 보낸 뒤 감시 DB에서 시작 ID 이후 기록을 읽어 JSON을 표준 출력에 씁니다. 아래 명령은 JSON을 PC의 임시 파일로 받은 뒤 캡처 성공 시에만 `observation.json`으로 바꿉니다.

```bat
if not exist monitor\backend\learning\data mkdir monitor\backend\learning\data
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 4 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson2
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson3
```

`lesson2`는 같은 JSON을 정규화하고 `lesson3`는 그 자료에서 조회 행을 선택합니다. 기대 사례는 원본 5행, 조회 4행, 기준 10에서 미해당입니다. 정규화에서는 404를 유지하고 조회 선택에서는 제외합니다. `observation.json`은 실행 시 생성하며 제출하지 않습니다.

## 화면 실습: 12회와 기준 10·20

Python 코드 변경은 API 재시작, 화면 코드는 web 이미지 재빌드가 필요합니다.

```bat
docker compose -f compose-monitor.yaml restart monitor-api
docker compose -f compose-monitor.yaml up -d --build monitor-web
docker compose -f compose-monitor.yaml restart monitor-gateway
```

감시 화면을 새로고침하고 로그인한 뒤 다음 순서로 진행합니다.

1. 기준 10 상태에서 **새 관찰 시작**을 누릅니다. 현재 최대 이벤트 ID가 경계로 저장됩니다.
2. 다른 탭에서 게시판을 새로고침하지 말고 다음 캡처를 실행합니다.

```bat
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 12 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
```

3. 1분 안에 감시 화면에서 **결과 불러오기**를 누릅니다. 예상값은 12·검토 후보이며, 조회 12행과 뒤따른 404 한 행이 근거로 표시됩니다.
4. 새 관찰을 다시 시작하지 않고 기준을 20으로 바꿔 **결과 불러오기**를 누릅니다. 기준시각과 ID가 같고 관찰값은 12, 판정은 기준 미해당이어야 합니다. 기준 10으로 복구해도 동일 자료를 사용합니다.
5. 새 관찰을 시작하고 새 일반 요청을 보내지 않은 상태에서 결과를 불러옵니다. 이전 DB 행을 지우지 않아도 새 ID 경계 뒤 관찰값이 0이어야 합니다.

결과 API는 `after_id` 이후이며 첫 결과 조회시각을 기준으로 직전 60초부터 그 시각까지 저장된 행을 읽습니다. 시작 버튼 이후 60초 동안 자동 수집하는 타이머가 아닙니다. 기준만 바꾸면 첫 결과의 `reference_time`과 `after_id`를 그대로 재사용합니다.

실패하거나 값이 예상과 다르면 일반 API의 전송 경고와 감시 API 로그를 확인하고 원인을 해결한 다음 새 관찰 → 캡처 → 1분 안의 첫 결과 순서로 다시 실행합니다. 터미널 출력만으로 DB 저장 성공을 판단하지 마세요. 확인이 필요하면 다음 조회로 실제 저장 행을 볼 수 있습니다.

```bat
docker compose -f compose-general.yaml logs --tail 20 general-api
docker compose -f compose-monitor.yaml logs --tail 20 monitor-api
docker compose -f compose-monitor.yaml exec monitor-db psql -U sample -d monitor_db -c "SELECT id, occurred_at, method, path, status_code, event_type FROM http_events ORDER BY id DESC LIMIT 15;"
```

4회 사례에서는 404가 정규화 결과에 남지만 조회 수에는 들지 않습니다. 12회 사례에서는 404가 마지막 목록 조회 뒤 30초 이내일 때만 문맥 근거가 됩니다. 실제 ID·시각 및 결과 행 수는 실행 조건에 따라 다릅니다. 직접 확인한 것과 예상만 한 것을 구분해 제출 시 기록하세요.

## 제출물

프로젝트 소스, 실행에 필요한 Dockerfile·Compose·gateway 설정, 의존성·잠금 파일, 기존 SQL 및 이 README를 GitHub 저장소 또는 ZIP으로 제출합니다. `.env`, 개인 계정 정보, 비밀번호·키·토큰, 실행 중 생성한 DB 데이터·로그, `node_modules`, `.next`, 가상환경·캐시는 제외합니다. 실제 요청 JSON, PCAP, 화면 캡처, 별도 검사 스크립트는 필수 제출물이 아닙니다.

## 선택 심화 실습

아래 네 항목은 필수 미션의 HTTP 근거 카드와 분리된 학습 활동입니다. 여기 적은 출력은 실행 전 예상값이며, 직접 실행한 뒤 실제 확인 상태를 별도로 기록하세요.

### 교육용 PCAP: 5초와 1초 구간

`learning.lesson_pcap`은 Python 표준 라이브러리만 사용해 합성 Ethernet/IPv4/UDP 프레임 6개를 만들고 임시 PCAP 파일에 씁니다. 읽기 코드는 패킷 타임스탬프를 첫 패킷 기준으로 구간 선택하고, 선택된 PCAP의 캡처 바이트 길이(`incl_len`) 합과 패킷 수를 계산합니다. PCAP은 실행 중 `/tmp`에 임시로 만들고 읽은 뒤 삭제합니다.

```bat
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson_pcap --window compare
```

예상 비교는 5초 구간에서 5패킷·225바이트, 1초 구간에서 2패킷·87바이트입니다. 5초는 오프셋 0.1, 0.5, 1.2, 2.5, 4.8초를 포함하고 5.2초 패킷은 제외합니다. 1초는 처음 두 패킷만 포함합니다. 바이트 값은 Ethernet 프레임 전체의 `incl_len` 합이며, IP 계층 payload만의 합은 아닙니다. 이 PCAP은 코드가 만든 교육용 UDP 패킷이고 실제 게시판 요청의 캡처가 아닙니다. HTTP 카드의 관찰값·근거와 합치지 않습니다.

### 문서용 IP의 IOC 문자열 비교

`learning.lesson_ioc`는 아래 실행으로 문서 예시 IP와 지표 문자열의 완전 일치 여부를 비교합니다. 실제 요청을 추적하거나 IP를 추측하지 않습니다.

```bat
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.lesson_ioc
```

예상 결과는 `198.51.100.20`이 지표 목록에 있어 `match=True`, `192.0.2.10`은 없어 `match=False`입니다. 이 주소들은 문서용 예시입니다. 감시 DB의 HTTP 원본에는 IP 필드가 없으므로 이 비교로 실제 요청·사용자·공격 여부를 식별할 수 없고, 결과를 HTTP 분석 카드에 적용하지 않습니다.

### 실제 요청 10회의 기준 경계

1. 감시 화면에서 기준값 10을 설정하고 **새 관찰 시작**을 누릅니다.
2. 다른 일반 게시판 요청을 만들지 않고 실제 10회 사례를 캡처합니다.

```bat
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 10 > monitor\backend\learning\data\observation-next.json && move /Y monitor\backend\learning\data\observation-next.json monitor\backend\learning\data\observation.json
```

3. 1분 안에 **결과 불러오기**를 누릅니다. 예상값은 관찰값 10, `검토 후보`, 조회 10행과 뒤따른 404 한 행을 합친 근거 11행입니다. `build_report`의 `count >= threshold`에서 10 >= 10이므로 기준을 충족합니다. 404는 `find_following_errors`에서 마지막 조회 이후 30초 이내인지 확인해 문맥 근거에만 포함하므로 조회 횟수에는 더하지 않습니다.
4. 기본 사례로 돌아가려면 **새 관찰 시작**을 다시 누르고 12회 캡처를 실행한 뒤 1분 안에 결과를 불러옵니다. 예상값은 기준 10에서 관찰값 12, 검토 후보, 12개 조회와 조건에 맞는 404 근거입니다. 이전 DB 행을 삭제하거나 JSON을 편집하지 않습니다.

실제 행 수가 다르면 추가 요청·시간 초과 여부를 확인하고 새 관찰부터 다시 실행합니다. 예상값을 실행 결과로 적지 말고 직접 확인 여부를 표시하세요.

PowerShell에서는 캡처 횟수를 바꾸어 아래처럼 실행합니다. 첫 명령이 실패하면 `throw`에서 중단하므로 이전 `observation.json`은 교체되지 않습니다.

```powershell
$next = "monitor\backend\learning\data\observation-next.json"
$observation = "monitor\backend\learning\data\observation.json"
docker compose -f compose-monitor.yaml exec -T monitor-api python -m learning.capture_case 10 | Set-Content -LiteralPath $next -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw "10회 캡처가 실패했습니다. 출력과 API 로그를 확인하세요." }
Move-Item -LiteralPath $next -Destination $observation -Force
```

기본 12회 사례로 복구할 때는 새 관찰을 시작한 뒤 위 명령의 마지막 숫자 `10`을 `12`로 바꾸어 다시 실행합니다.

### AI 분석 후보 코드 검토

다음은 검토 연습용 순수 분석 후보입니다. 실제 로그나 비밀값 없이 함수 로직만 평가합니다.

```python
def candidate(events, threshold):
    views = [e for e in events if e["method"] == "GET" and e["path"] == "/"
             and e["status_code"] == 200 and e["kind"] == "post_list"]
    errors = [e for e in events if e["status_code"] == 404]
    count = len(views) + len(errors)
    return count >= threshold, views + errors
```

| 검토 항목 | 후보 코드의 문제/장점 | 현재 구현과 결정 |
|---|---|---|
| 조회 조건 | GET·`/`·200·`post_list` 네 조건을 모두 적용함 | `select_views`가 같은 네 조건을 적용하므로 이 부분은 채택 |
| 404 문맥 | 모든 404를 고르고 조회 수에 더하며 시간 조건이 없음 | 거절. `find_following_errors`에서 마지막 조회 이후 `0 < gap <= 30`초인 404만 선택하고, 조회가 없으면 빈 목록을 반환 |
| 기준 경계 | `>=` 비교를 사용함 | 이 연산은 채택. `build_report`가 조회 수만으로 `count >= threshold`를 계산하므로 10회/기준 10은 후보, 12회/기준 20은 미해당 |
| 근거 일관성 | 결과 근거에 조회와 오류를 넣지만 ID를 분리하지 않고 조회 수에도 오류를 섞음 | 수정. 현재 보고서는 같은 `views` 목록에서 횟수와 조회 ID를 만들고, 조건을 통과한 오류만 별도 문맥 근거와 evidence ID에 추가 |

이 비교는 교육용 후보에 대한 코드 검토입니다. 실제 AI 도구에서 받은 후보가 따로 있다면 그 코드를 실제 분석 함수와 대조하고, 실행 로그·계정·토큰은 AI 입력으로 보내지 마세요. PCAP과 IOC 예시는 HTTP 카드의 입력이나 근거로 사용하지 않습니다.
