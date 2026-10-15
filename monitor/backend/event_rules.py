from datetime import datetime
from uuid import UUID

EVENT_TYPES = {
    "login_success", "login_failure", "logout_request", "http_request",
    "post_list", "post_view", "post_create_request",
    "post_update_request", "post_delete_request", "request_error",
}


def make_event(data):
    if not isinstance(data, dict):
        return None
    method = data.get("method")
    path = data.get("path")
    status = data.get("status_code")
    allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
    if not isinstance(method, str) or method not in allowed_methods:
        return None
    if not isinstance(path, str) or not path.startswith("/") or len(path) > 500:
        return None
    if type(status) is not int or not 100 <= status <= 599:
        return None

    parts = path.strip("/").split("/")
    post_detail = len(parts) == 2 and parts[0] in {"board", "posts"} and parts[1].isdecimal()
    post_action = len(parts) == 3 and parts[0] == "board" and parts[1].isdecimal()
    login_path = path in {"/auth/login", "/api/auth/login"}
    if method == "POST" and login_path and status == 200:
        event_type = "login_success"
    elif method == "POST" and login_path and status == 401:
        event_type = "login_failure"
    elif method == "POST" and path in {"/logout", "/api/auth/logout"}:
        event_type = "logout_request"
    elif method == "POST" and path == "/board/new":
        event_type = "post_create_request"
    elif method == "POST" and post_action and parts[2] == "edit":
        event_type = "post_update_request"
    elif method == "POST" and post_action and parts[2] == "delete":
        event_type = "post_delete_request"
    elif status >= 400:
        event_type = "request_error"
    elif method == "GET" and path == "/" and status == 200:
        event_type = "post_list"
    elif method == "GET" and post_detail and status == 200:
        event_type = "post_view"
    else:
        event_type = "http_request"
    attempted_username = data.get("attempted_username") if login_path else None
    if not isinstance(attempted_username, str) or not attempted_username.strip():
        attempted_username = None
    else:
        attempted_username = attempted_username.strip()[:100]
    source_event_id = data.get("event_id")
    if not isinstance(source_event_id, str) or not source_event_id or not login_path:
        source_event_id = None
    else:
        try:
            source_event_id = str(UUID(source_event_id))
        except ValueError:
            source_event_id = None
    source_occurred_at = data.get("occurred_at") if source_event_id else None
    if source_occurred_at is not None:
        try:
            parsed = datetime.fromisoformat(source_occurred_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                source_occurred_at = None
        except (AttributeError, TypeError, ValueError):
            source_occurred_at = None
    return {"method": method, "path": path, "status_code": status,
            "event_type": event_type, "attempted_username": attempted_username,
            "source_event_id": source_event_id, "source_occurred_at": source_occurred_at}
