import json
import requests
from flask import Flask, request
from routes.posts import posts_bp
from routes.auth import auth_bp

app = Flask(__name__)
app.json.ensure_ascii = False
MONITOR_URL = "http://127.0.0.1:5200/api/events"

app.register_blueprint(posts_bp)
app.register_blueprint(auth_bp)


@app.after_request
def record_request(response):
    event = {
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
    }
    print(json.dumps(event, ensure_ascii=False), flush=True)
    try:
        result = requests.post(MONITOR_URL, json=event, timeout=0.5)
        result.raise_for_status()
    except requests.RequestException:
        app.logger.warning("감시 서비스에 요청 기록을 보내지 못했습니다.")
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5100)
