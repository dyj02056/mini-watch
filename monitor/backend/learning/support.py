from datetime import datetime, timedelta, timezone

from repositories.events import events_after, latest_event_id


def begin_observation():
    return {"after_id": latest_event_id(), "reference_time": None}


def load_observation(after_id, reference_time=None):
    # The first result request fixes the reference time for later threshold comparisons.
    reference = datetime.fromisoformat(reference_time) if reference_time else datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    since = reference - timedelta(seconds=60)
    rows = events_after(after_id, since, reference)
    return reference.isoformat(), rows
