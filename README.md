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
