import os
from pathlib import Path
from dotenv import load_dotenv

# 로컬 개발 및 스크립트 실행 시 .env 파일 로드 (Render 환경에서는 시스템 환경 변수가 우선 적용됨)
load_dotenv(Path(__file__).with_name(".env"))

from flask import Flask
from routes.posts import posts_bp
from routes.auth import auth_bp
from auth_helpers import configure_session, no_cache, template_auth
from error_handlers import register_error_handlers
from request_logging import record_request
from observability import init_observability

init_observability()

app = Flask(__name__)
app.json.ensure_ascii = False
configure_session(app, "general_session")
app.register_blueprint(posts_bp)
app.register_blueprint(auth_bp)
app.context_processor(template_auth)
register_error_handlers(app)
app.after_request(no_cache)
app.after_request(record_request)


@app.get("/health")
def health():
    return {"service": "general", "status": "ok"}


@app.get("/api/sentry-test")
def sentry_test():
    """Sentry 연동 확인용 경로. ENABLE_SENTRY_TEST=true일 때만 오류를 발생시킵니다.
    실습 후에는 반드시 ENABLE_SENTRY_TEST=false로 되돌립니다."""
    from auth_helpers import current_user
    if current_user() is None:
        return {"error": "로그인이 필요합니다."}, 401
    if os.environ.get("ENABLE_SENTRY_TEST", "false").lower() != "true":
        return {"message": "sentry-test가 비활성화되어 있습니다. ENABLE_SENTRY_TEST=true로 설정하면 활성화됩니다."}
    # 의도적인 오류 제거: 기존 1/0 오류를 정상 JSON 반환으로 수정
    # 수정 전: return 1 / 0  (ZeroDivisionError 발생)
    # 수정 후: 정상 JSON 반환
    return {"message": "sentry-test 요청을 정상적으로 처리했습니다.", "status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
