from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from hashlib import sha256

THRESHOLD = 3
WINDOW_SECONDS = 60
LOGIN_PATHS = frozenset({"/auth/login", "/api/auth/login"})
RULE = {
    "id": "repeated-auth-failure",
    "threshold": THRESHOLD,
    "window_seconds": WINDOW_SECONDS,
    "source": "app",
}


def parse_time(value):
    if isinstance(value, datetime):
        moment = value
    elif isinstance(value, str):
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("발생 시각을 읽을 수 없습니다.")
    if moment.tzinfo is None:
        raise ValueError("발생 시각에 시간대가 없습니다.")
    return moment.astimezone(timezone.utc)


def normalize_auth_event(row):
    if row.get("event_type") not in {"login_failure", "login_success"}:
        return None
    if row.get("method") != "POST" or row.get("path") not in LOGIN_PATHS:
        return None
    if not isinstance(row.get("attempted_username"), str) or not row["attempted_username"].strip():
        return None
    failure = row["event_type"] == "login_failure"
    if row.get("status_code") != (401 if failure else 200):
        return None
    event = dict(row)
    event["event_id"] = row.get("source_event_id") or f"http-{row['id']}"
    event["event_type"] = "auth_failure" if failure else "auth_success"
    event["source"] = "app"
    event["raw"] = dict(row)
    parse_time(event["occurred_at"])
    return event


def build_detection(rows, observation, now, invalid_line_count=0):
    selected = []
    seen = set()
    started_at = parse_time(observation["started_at"]) if observation else None
    for row in rows:
        event = normalize_auth_event(row)
        if event is None:
            continue
        occurred_at = parse_time(event["occurred_at"])
        if started_at and started_at <= occurred_at <= now and event["event_id"] not in seen:
            selected.append(event)
            seen.add(event["event_id"])
    selected.sort(key=lambda item: (parse_time(item["occurred_at"]), item["event_id"]))

    counts = defaultdict(int)
    cutoff = now - timedelta(seconds=WINDOW_SECONDS)
    for event in selected:
        if event["event_type"] == "auth_failure" and parse_time(event["occurred_at"]) >= cutoff:
            counts[event["attempted_username"]] += 1

    windows = defaultdict(deque)
    alerted = set()
    alerts = []
    for event in selected:
        if event["event_type"] != "auth_failure":
            continue
        username = event["attempted_username"]
        moment = parse_time(event["occurred_at"])
        window = windows[username]
        while window and parse_time(window[0]["occurred_at"]) < moment - timedelta(seconds=WINDOW_SECONDS):
            window.popleft()
        window.append(event)
        if len(window) >= THRESHOLD and username not in alerted:
            identifier = sha256(f"{observation['id']}:{username}".encode("utf-8")).hexdigest()[:20]
            evidence = list(window)
            alerts.append({
                "id": f"auth-{identifier}",
                "attempted_username": username,
                "created_at": event["occurred_at"],
                "failure_count": len(evidence),
                "window_seconds": WINDOW_SECONDS,
                "evidence_event_ids": [item["event_id"] for item in evidence],
                "evidence": evidence,
            })
            alerted.add(username)

    return {
        "observation": observation,
        "rule": RULE,
        "counts": [{"attempted_username": name, "failure_count": count}
                   for name, count in sorted(counts.items())],
        "events": selected,
        "alerts": alerts,
        "evaluated_at": now.isoformat(timespec="microseconds"),
        "invalid_line_count": invalid_line_count,
    }
