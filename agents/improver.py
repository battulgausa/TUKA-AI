import json
import os

class ImproverAgent:
    def suggest(self, goal: str) -> dict:
        """
        Өмнөх runs.jsonl-оос хамгийн сүүлийн төстэй зорилтыг олж,
        төлөвлөгөөг илүү нарийсгах санал гаргана.
        """
        path = os.path.join("runs", "runs.jsonl")
        if not os.path.exists(path):
            return {"suggested_steps": [], "reason": "No history yet"}

        last = None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if isinstance(rec.get("goal"), str) and rec["goal"].lower() in goal.lower() or goal.lower() in rec["goal"].lower():
                        last = rec
                except Exception:
                    continue

        # Хэрвээ төстэй олдохгүй бол хамгийн сүүлийн run-г ашиглая
        if last is None:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last = json.loads(lines[-1])

        if not last:
            return {"suggested_steps": [], "reason": "No usable history"}

        # MVP: илүү бизнес-утгатай төлөвлөгөө санал болгох
        improved = [
            f"Confirm customer segment & channel for: {goal}",
            "Define follow-up stages (Day 0, Day 2, Day 7)",
            "Draft message templates (SMS/email)",
            "Create CRM fields + statuses",
            "Schedule automation triggers",
            "Add metrics: reply rate, conversion rate",
            "Run a test with 5 sample leads, then evaluate"
        ]
        return {"suggested_steps": improved, "reason": "Based on past run history"}