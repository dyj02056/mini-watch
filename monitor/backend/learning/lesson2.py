import json
from pathlib import Path

from learning.normalize import normalize_events

path = Path(__file__).parent / "data" / "observation.json"
data = json.loads(path.read_text(encoding="utf-8"))
events = normalize_events(data["events"])
print(json.dumps(events, ensure_ascii=False, indent=2))
