import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def init_observability():
    """Sentry 오류 수집 초기화. 개발·Waitress 실행 모두에서 호출됩니다."""
    dsn = os.environ.get("SENTRY_DSN", "")
    if not dsn:
        return  # DSN이 없으면 Sentry를 비활성화합니다.

    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        environment=os.environ.get("SENTRY_ENVIRONMENT", "mini-monitor"),
        release=os.environ.get("APP_VERSION", "0.0.0"),
        # PII(개인 식별 정보) 제외: 요청 본문·쿠키·헤더·사용자 정보를 전송하지 않습니다.
        send_default_pii=False,
        traces_sample_rate=0.0,
    )
