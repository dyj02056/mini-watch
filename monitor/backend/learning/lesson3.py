import json
from pathlib import Path

from learning.http_rules import select_views
from learning.normalize import normalize_events
from learning.report import build_report

path = Path(__file__).parent / "data" / "observation.json"
data = json.loads(path.read_text(encoding="utf-8-sig"))
events = normalize_events(data["events"])
views = select_views(events)
print(json.dumps({"normalized_count": len(events), "view_count": len(views), "view_ids": [row["id"] for row in views], "report_at_10": build_report(events, 10)["cards"][0]}, ensure_ascii=False, indent=2))
