import json
import os
from datetime import datetime

def log_run(goal: str, plan: list, result: dict, evaluation: dict):
    os.makedirs("runs", exist_ok=True)
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "goal": goal,
        "plan": plan,
        "result": result,
        "evaluation": evaluation,
    }
    with open(os.path.join("runs", "runs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")