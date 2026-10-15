from learning.log_data import read_logs
from learning.normalize_app import normalize_app
from learning.normalize_nginx import normalize_nginx


def load_normalized_events():
    logs = read_logs()
    events = [normalize_app(event, index) for index, event in enumerate(logs["app"], start=1)]
    events.extend(normalize_nginx(line, index) for index, line in enumerate(logs["nginx"], start=1))
    return events
