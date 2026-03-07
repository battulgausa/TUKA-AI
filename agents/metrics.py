import json
import os
import random
from datetime import datetime
from tools.crm_store import read_db, add_lead

METRICS_PATH = os.path.join("data", "metrics.json")

class MetricsAgent:
    def handle(self, step: str) -> dict:
        s = (step or "").lower()
        os.makedirs("data", exist_ok=True)

        # KPI targets
        if "add metrics" in s:
            metrics = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "kpis": [
                    {"name": "reply_rate", "target": 0.25},
                    {"name": "conversion_rate", "target": 0.10},
                ]
            }
            with open(METRICS_PATH, "w", encoding="utf-8") as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
            return {"status": "ok", "metrics": metrics}

        # 5 lead test simulation
        if "run a test with 5 sample leads" in s:
            db = read_db()
            leads = db.get("leads", [])

            if len(leads) < 5:
                for i in range(5 - len(leads)):
                    add_lead(f"Test Lead {len(leads)+i+1}", "email")

            replies = 0
            conversions = 0
            for _ in range(5):
                if random.random() < 0.40:
                    replies += 1
                if random.random() < 0.20:
                    conversions += 1

            result = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "sample_size": 5,
                "reply_rate": round(replies / 5, 2),
                "conversion_rate": round(conversions / 5, 2),
            }

            with open(METRICS_PATH, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            return {"status": "ok", "simulation": result}

        return {"status": "skip"}
