# Mini Watch Day5 시작 코드

Day4 본문 6교시에서 완성한 코드를 새 Day5 폴더로 받아 사용한다.

- general: Flask/Jinja2 일반 게시판.
- monitor/backend: 계정 확인, 관찰 메모 CRUD, 요청 기록 수집·조회 API.
- monitor/frontend: React/Vite 감시 대시보드와 분리된 컴포넌트·API 모듈.

## 새 Day5 폴더로 받기

VS Code에서 C:\work 같은 상위 폴더를 열고 새 CMD에서 실행한다.

```text
git clone --branch day05-start --single-branch https://github.com/zeroskill2400/mini-watch.git mini-watch-day05
```

받은 mini-watch-day05 폴더를 VS Code로 열고 새 CMD를 연다. 먼저 시작 브랜치를 확인한다.

```text
git status
```

1~3교시는 짧은 문서로 Git 협업을 연습한다. 공통 기준은 받은 이름 그대로 day05-start를 사용한다.

- 1교시: 내 PC에서 민수·지연 역할을 번갈아 맡는다. 같은 기준에서 feature/minsu와 feature/jiyun을 만들고, 각자 문서를 커밋한다. 브랜치를 오가며 비교한 뒤 day05-start에 두 작업을 병합한다.
- 2교시: 실제 두 사람이 같은 폴더에서 이어간다. 민수가 빈 팀 저장소에 1교시 결과를 올리고, 지연은 자신의 연습 기록을 practice/day05로 남긴 뒤 팀 기준을 받는다. 새 작업 브랜치를 push하고 서로 PR을 리뷰·병합한 뒤 모두 pull한다.
- 3교시: 같은 점검표 제목을 다르게 수정한다. 먼저 병합된 기준을 다른 작업 브랜치에 받아 충돌을 해결하고, 같은 PR에 올려 리뷰·병합한 뒤 모두 최신 결과를 받는다.

브랜치를 만들기 전에 현재 브랜치를 확인하고, 전환하기 전에 수정 내용을 커밋한다. 병합할 때는 작업을 받을 브랜치로 먼저 이동한다. 명령과 전체 파일 내용은 각 교안의 순서대로 진행한다.

팀 원격은 team이라는 별명으로 추가한다. origin은 강사 저장소로 남겨 두며 학생 변경을 강사 저장소로 push하지 않는다. 1~3교시는 서버와 DB를 켜지 않아도 된다.

4~6교시는 Next.js를 작은 페이지부터 시작해 기존 서비스 API와 연결한다. 세부 실행 안내는 해당 교안에서 이어간다.

## 다음 교시로 이어갈 상태

감시 로그인은 Flask의 DB 계정 확인 후 React state로 화면을 전환한다. 새로고침하면 로그인 폼으로 돌아오며, 이 로컬 학습판은 서버 API의 세션 접근 보호를 포함하지 않는다.

앱을 실행할 때는 서비스별로 .env·가상환경과 npm 의존성을 준비한다. 기존 general_db·monitor_db는 그대로 사용하며, Git clone은 실제 DB 데이터를 복사하지 않는다. SQL·설정 예시는 각 서버 폴더에 있다.

쿠키·세션 확장 부록 완성본은 별도의 day04-session 브랜치에서 받을 수 있다.
