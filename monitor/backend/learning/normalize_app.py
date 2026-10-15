def normalize_app(event, number):
    return {
        "id": f"app-{number}", "source": "app", "method": event["method"],
        "path": event["path"], "status_code": int(event["status_code"]), "raw": event,
    }
