from learning.http_rules import find_following_errors, select_views
from learning.merge import load_normalized_events


def build_report(events, threshold):
    views = select_views(events)
    errors = find_following_errors(events, views)
    count = len(views)
    candidate = count >= threshold
    evidence = views + errors
    return {
        "cards": [{
            "source": "http_live",
            "observed": count,
            "threshold": threshold,
            "verdict": "검토 후보" if candidate else "기준 미해당",
            "candidate": candidate,
            "reason": f"GET / 200 post_list {count}건을 기준 {threshold}와 비교했습니다. 뒤따른 404는 횟수에 포함하지 않습니다.",
            "view_ids": [item["id"] for item in views],
            "error_ids": [item["id"] for item in errors],
            "evidence_ids": [item["id"] for item in evidence],
            "records": evidence,
        }],
    }


def build_raw_report():
    events = load_normalized_events()
    return {
        "ready": True,
        "events": events,
        "total_count": len(events),
        "error_count": sum(event["status_code"] >= 400 for event in events),
    }
