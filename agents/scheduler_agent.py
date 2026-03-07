from tools.crm_store import read_db
from tools.scheduler import enqueue_followups, run_due

class SchedulerAgent:
    def enqueue(self):
        db = read_db()
        # Use first workflow for now
        wf = db.get("workflows", [])[0] if db.get("workflows") else {"name": "CRM Follow-up", "stages": [0,2,7]}
        leads = db.get("leads", [])

        raw = wf.get("stages", [0, 2, 7])
        stages = []
        for s in raw:
            if isinstance(s, int):
                stages.append(s)
            else:
                digits = "".join(ch for ch in str(s) if ch.isdigit())
                stages.append(int(digits) if digits else 0)

        return enqueue_followups(wf["name"], leads, stages)

    def run_due(self):
        return run_due()
