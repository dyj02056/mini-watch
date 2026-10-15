from datetime import datetime, timezone
import json
from uuid import uuid4

from flask import Blueprint

from auth_helpers import api_access_error
from detection_rules import build_detection
from learning.log_data import read_complete_lines
from repositories import events as event_repository
from repositories import observations as observation_repository

detection_bp = Blueprint("detection", __name__)


def invalid_app_line_count():
    invalid_line_count = 0
    for line in read_complete_lines("app.jsonl"):
        try:
            json.loads(line)
        except (json.JSONDecodeError, UnicodeError):
            invalid_line_count += 1
    return invalid_line_count


def read_detection(observation=None):
    observation = observation if observation is not None else observation_repository.current_observation()
    now = datetime.now(timezone.utc)
    invalid_line_count = invalid_app_line_count()
    if observation is None:
        return build_detection([], None, now, invalid_line_count)
    rows = event_repository.events_after(
        observation["after_id"], observation["started_at"], now
    )
    return build_detection(rows, observation, now, invalid_line_count)


@detection_bp.post("/api/detection/start")
def start_detection():
    error = api_access_error()
    if error:
        return error
    observation = {
        "id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        "after_id": event_repository.latest_event_id(),
    }
    observation_repository.create_observation(observation)
    return read_detection(observation), 201


@detection_bp.get("/api/detection")
def get_detection():
    error = api_access_error()
    if error:
        return error
    return read_detection()
