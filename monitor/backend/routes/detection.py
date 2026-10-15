from datetime import datetime, timedelta, timezone

from flask import Blueprint, request

from auth_helpers import api_access_error
from repositories import events as event_repository

detection_bp = Blueprint("detection", __name__)
THRESHOLD = 3
WINDOW_SECONDS = 60


@detection_bp.post("/api/detection/start")
def start_detection():
    error = api_access_error()
    if error:
        return error
    return {
        "after_id": event_repository.latest_event_id(),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }


@detection_bp.get("/api/detection")
def get_detection():
    error = api_access_error()
    if error:
        return error
    try:
        after_id = int(request.args.get("after_id", ""))
        started_at = datetime.fromisoformat(request.args.get("started_at", "").replace("Z", "+00:00"))
        if after_id < 0:
            raise ValueError
    except (TypeError, ValueError):
        return {"error": "관찰 시작 정보가 올바르지 않습니다."}, 400
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    rows = event_repository.events_after(after_id, started_at, now)
    failures = [row for row in rows if row["event_type"] == "login_failure"
                and row.get("attempted_username")]
    by_username = {}
    for event in failures:
        by_username.setdefault(event["attempted_username"], []).append(event)

    alerts = []
    for username, events in by_username.items():
        for index, first in enumerate(events):
            evidence = [first]
            first_time = datetime.fromisoformat(first["occurred_at"].replace("Z", "+00:00"))
            for candidate in events[index + 1:]:
                timestamp = datetime.fromisoformat(candidate["occurred_at"].replace("Z", "+00:00"))
                if timestamp - first_time <= timedelta(seconds=WINDOW_SECONDS):
                    evidence.append(candidate)
                else:
                    break
            if len(evidence) >= THRESHOLD:
                alerts.append({"attempted_username": username, "occurred_at": first["occurred_at"],
                               "events": evidence[:THRESHOLD]})
                break

    cutoff = now - timedelta(seconds=WINDOW_SECONDS)
    recent_counts = {}
    for event in failures:
        timestamp = datetime.fromisoformat(event["occurred_at"].replace("Z", "+00:00"))
        if timestamp >= cutoff:
            recent_counts[event["attempted_username"]] = recent_counts.get(event["attempted_username"], 0) + 1

    return {
        "observation": {"after_id": after_id, "started_at": started_at.isoformat()},
        "rule": {"threshold": THRESHOLD, "window_seconds": WINDOW_SECONDS},
        "counts": [{"attempted_username": username, "count": count}
                   for username, count in sorted(recent_counts.items())],
        "alerts": alerts,
    }
