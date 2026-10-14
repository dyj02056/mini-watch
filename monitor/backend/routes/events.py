import hmac
import os
from flask import Blueprint, request
from auth_helpers import api_access_error
from event_rules import make_event
from repositories import events as event_repository

events_bp = Blueprint("events", __name__)


@events_bp.get("/health")
def health():
    return {"service": "monitor", "status": "ok"}


@events_bp.post("/api/events")
def receive_event():
    """일반 Flask가 보내는 요청 기록을 받습니다. EVENT_TOKEN으로 발신자를 검증합니다."""
    token = os.environ.get("EVENT_TOKEN", "")
    if token:
        incoming = request.headers.get("X-Event-Token", "")
        if not (
            isinstance(incoming, str)
            and isinstance(token, str)
            and hmac.compare_digest(incoming.encode(), token.encode())
        ):
            return {"error": "인증되지 않은 요청입니다."}, 401

    event = make_event(request.get_json(silent=True))
    if event is None:
        return {"error": "method, path, status_code를 올바르게 보내 주세요."}, 400
    event_repository.create_event(event)
    return {"message": "기록을 받았습니다."}, 201


@events_bp.get("/api/events")
def get_events():
    error = api_access_error()
    if error:
        return error
    event_type = request.args.get("event_type")
    allowed = {"login_success", "login_failure", "http_request", "post_list", "request_error"}
    if event_type is not None and event_type not in allowed:
        return {"error": "지원하지 않는 이벤트 종류입니다."}, 400
    return {"events": event_repository.list_events(event_type)}
