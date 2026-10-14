from datetime import datetime


def select_views(events):
    return [
        event for event in events
        if event.get("method") == "GET"
        and event.get("path") == "/"
        and event.get("status_code") == 200
        and event.get("kind") == "post_list"
    ]


def find_following_errors(events, selected_views):
    if not selected_views:
        return []
    last_view = max(selected_views, key=lambda item: item["received_at"])
    last_time = datetime.fromisoformat(last_view["received_at"])
    following = []
    for event in events:
        if event.get("status_code") != 404:
            continue
        event_time = datetime.fromisoformat(event["received_at"])
        gap = (event_time - last_time).total_seconds()
        if 0 < gap <= 30:
            following.append(event)
    return following
