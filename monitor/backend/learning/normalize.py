def normalize_event(event):
    """Copy a database event into the common learning format."""
    normalized = dict(event)
    normalized["id"] = f"http-{event['id']}"
    normalized["source"] = "http_live"
    normalized["kind"] = event["event_type"]
    normalized["received_at"] = event["occurred_at"]
    return normalized


def normalize_events(events):
    return [normalize_event(event) for event in events]
