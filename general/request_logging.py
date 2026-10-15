import json
import os
import requests
from flask import current_app, request

def record_request(response):
    event = {
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
    }
    # Login evidence needs the submitted account name, never the password.
    if request.method == "POST" and request.path in {"/auth/login", "/api/auth/login"}:
        data = request.get_json(silent=True)
        username = data.get("username") if isinstance(data, dict) else request.form.get("username")
        if isinstance(username, str):
            event["attempted_username"] = username.strip()[:100]
    print(json.dumps(event, ensure_ascii=False), flush=True)
    try:
        monitor_url = os.environ.get("MONITOR_URL", "http://monitor-api:5000/api/events")
        token = os.environ.get("EVENT_TOKEN", "")
        headers = {"X-Event-Token": token} if token else {}
        result = requests.post(monitor_url, json=event, headers=headers, timeout=2)
        result.raise_for_status()
    except requests.RequestException:
        current_app.logger.warning("감시 서비스에 요청 기록을 보내지 못했습니다.")
    return response
