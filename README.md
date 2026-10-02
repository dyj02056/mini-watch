<<<<<<< HEAD
# Mini Watch

일반 서비스와 감시 서비스를 만든다.

## 수업 코드 받기

| 자료 | 내용 |
| --- | --- |
| [2일차 시작 코드](https://github.com/zeroskill2400/mini-watch/tree/day02-start) | 게시글 조회와 요청 전달을 하는 작은 Flask 앱 두 개 |
| [3일차 시작 코드](https://github.com/zeroskill2400/mini-watch/tree/day03-start) | 2일차에 완성한 PostgreSQL·로그인·세션·감시 기록 코드 |

날짜별 시작 코드를 제공한다. **3일차 시작 코드는 2일차 완성 상태와 같다.**

처음 시작할 때는 아래 명령으로 2일차 시작본을 받는다. 이전 실습 폴더와 다른 상위 폴더에서 실행한다.

```text
git clone --branch day02-start https://github.com/zeroskill2400/mini-watch.git mini-watch
```

복제가 끝나면 `mini-watch` 폴더를 VS Code로 열고 그 안의 README를 따라 일반 서비스와 감시 서비스를 실행한다. Windows 명령 프롬프트(cmd)를 사용하며, 패키지는 서비스별 `requirements.txt`로 설치한다.

수업 중에는 같은 폴더를 계속 사용한다. 다음 수업의 시작 코드와 비교하거나 다시 준비해야 할 때만 별도 폴더에 받는다.

```text
git clone --branch day03-start https://github.com/zeroskill2400/mini-watch.git mini-watch-day03-start
```

Git에는 소스·SQL·설정 예시가 들어 있다. 실제 `.env`, 가상환경, PostgreSQL의 데이터는 포함하지 않으므로 받은 코드의 README 순서대로 준비한다.

`main`의 기존 코드는 1일차 실습 기록이다. 2일차 수업은 위의 시작 브랜치로 진행한다.
=======
# mini-watch 2일차 시작 코드

`day02-start`는 2일차 1교시에서 사용할 작은 시작 코드다. `general`은 게시글을 보여 주고, `monitor/backend`는 일반 서비스에 요청을 전달한다. 이번 브랜치에는 아직 DB 연결 기능이 없다.

복제한 프로젝트 폴더를 VS Code에서 연다. `Ctrl+Shift+P` → `Terminal: Select Default Profile` → **Command Prompt(명령 프롬프트, CMD)**를 선택하고 새 터미널을 연다.

## 일반 서비스 실행

VS Code의 **general 폴더를 오른쪽 클릭 → 통합 터미널에서 열기**를 선택한다. CMD에서 이 폴더의 가상환경을 처음 한 번 만든다.

```text
python -m venv venv
```

가상환경을 켠다. 입력 줄 앞에 `(venv)`가 붙으면 켜진 것이다.

```text
venv\Scripts\activate
```

패키지 목록을 설치한다.

```text
python -m pip install -r requirements.txt
```

일반 서버를 실행한다. 이 창은 켜 둔다.

```text
python app.py
```

크롬에서 http://127.0.0.1:5100/posts/1 을 열면 1번 게시글이 나온다.

## 감시 서비스 실행

VS Code의 **monitor 아래 backend 폴더를 오른쪽 클릭 → 통합 터미널에서 열기**로 별도의 CMD를 연다. 이 폴더에도 가상환경을 처음 한 번 만든다.

```text
python -m venv venv
```

가상환경을 켠다.

```text
venv\Scripts\activate
```

`(venv)`를 확인하고 패키지 목록을 설치한다.

```text
python -m pip install -r requirements.txt
```

감시 서버를 실행한다.

```text
python app.py
```

크롬에서 http://127.0.0.1:5200/posts/1 을 열면 일반 서버와 같은 게시글이 나온다.

새 CMD를 열 때는 해당 서비스 폴더에서 가상환경을 다시 켠다. 서버 코드를 고치면 저장한 뒤 서버 창에서 `Ctrl+C`로 멈추고 `python app.py`로 다시 실행한다.

## 수업 이어가기

이 폴더에서 1교시부터 차례로 기능을 붙인다. `day03-start` 브랜치에는 3일차 시작 코드(2일차 완성 상태)와 DB 준비·실행 안내가 있다.

`venv`, Python 캐시와 실제 `.env`는 Git에 포함하지 않는다. 패키지는 서비스별 `requirements.txt`로 각 컴퓨터에서 설치한다.
>>>>>>> origin/day02-start
