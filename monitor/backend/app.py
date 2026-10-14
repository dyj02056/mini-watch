import os
from pathlib import Path
from dotenv import load_dotenv

# 로컬 개발 및 스크립트 실행 시 .env 파일 로드 (Render 환경에서는 시스템 환경 변수가 우선 적용됨)
load_dotenv(Path(__file__).with_name(".env"))

from flask import Flask
from routes.auth import auth_bp
from routes.events import events_bp
from routes.analysis import analysis_bp
from routes.notes import notes_bp
from auth_helpers import configure_session, no_cache
from error_handlers import register_error_handlers
from observability import init_observability

init_observability()

app = Flask(__name__)
app.json.ensure_ascii = False
configure_session(app, "monitor_session")
app.register_blueprint(auth_bp)
app.register_blueprint(events_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(notes_bp)
register_error_handlers(app)
app.after_request(no_cache)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
