import datetime
import json
import pathlib

HIST = pathlib.Path("results/metric_history.json")
CURR = json.loads(pathlib.Path("results/humaneval_latest.json").read_text())

history = []
if HIST.exists():
    history = json.loads(HIST.read_text())

history.append({"ts": datetime.datetime.utcnow().isoformat(), **CURR})
HIST.write_text(json.dumps(history, indent=2))
