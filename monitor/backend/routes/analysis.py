from datetime import datetime

from flask import Blueprint, request

from auth_helpers import api_access_error
from learning.normalize import normalize_events
from learning.report import build_raw_report, build_report
from learning.support import begin_observation, load_observation

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.get("/api/analysis/raw")
def get_raw_logs():
    error = api_access_error()
    if error:
        return error
    try:
        return build_raw_report()
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {"error": str(error)}, 400


@analysis_bp.post("/api/analysis/start")
def start_analysis():
    error = api_access_error()
    if error:
        return error
    return begin_observation()


@analysis_bp.get("/api/analysis")
def get_analysis():
    error = api_access_error()
    if error:
        return error
    after_id_raw = request.args.get("after_id", "")
    threshold_raw = request.args.get("threshold", "")
    reference_time = request.args.get("reference_time")
    try:
        after_id = int(after_id_raw)
        threshold = int(threshold_raw)
        if after_id < 0 or not 1 <= threshold <= 10000:
            raise ValueError
        if reference_time:
            datetime.fromisoformat(reference_time.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return {"error": "after_id, threshold 또는 reference_time 값이 올바르지 않습니다."}, 400
    reference, rows = load_observation(after_id, reference_time)
    normalized = normalize_events(rows)
    report = build_report(normalized, threshold)
    return {"after_id": after_id, "reference_time": reference, "records": normalized, **report}
