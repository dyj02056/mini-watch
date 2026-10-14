"""Send real requests through the local general service and print their DB rows."""
import json
import sys
import time

import requests

from learning.support import begin_observation
from repositories.events import events_after


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    if not 1 <= count <= 100:
        raise SystemExit("요청 횟수는 1~100이어야 합니다.")
    base_url = "http://general-api:5000"
    start = begin_observation()
    for _ in range(count):
        response = requests.get(f"{base_url}/", timeout=5)
        response.raise_for_status()
        time.sleep(0.15)
    missing = requests.get(f"{base_url}/training-missing", timeout=5)
    if missing.status_code != 404:
        raise SystemExit(f"없는 경로가 404가 아닙니다: {missing.status_code}")
    # Give the after_request POST a moment to commit in the monitor database.
    time.sleep(0.3)
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(minutes=5)
    rows = events_after(start["after_id"], since, datetime.now(timezone.utc))
    observation = {"after_id": start["after_id"], "events": rows}
    print(json.dumps(observation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
