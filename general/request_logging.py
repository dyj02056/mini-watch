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
    print(json.dumps(event, ensure_ascii=False), flush=True)
    try:
        monitor_url = os.environ.get("MONITOR_URL", "http://monitor-api:5000/api/events")
        result = requests.post(monitor_url, json=event, timeout=2)
        result.raise_for_status()
    except requests.RequestException:
        current_app.logger.warning("감시 서비스에 요청 기록을 보내지 못했습니다.")
    return response
