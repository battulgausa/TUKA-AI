import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB = Path("data/queue.json")

def _now_utc():
    return datetime.now(timezone.utc)

def _load():
    if not DB.exists():
        return {"jobs": []}
    return json.loads(DB.read_text(encoding="utf-8"))

def _save(db):
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.write_text(json.dumps(db, indent=2), encoding="utf-8")

def enqueue_followups(workflow_name, leads, stages):
    db = _load()
    now = _now_utc()

    campaign_id = f"camp_{now.strftime('%Y%m%d_%H%M%S')}"

    added = 0

    for lead in leads:
        for day in stages:
            due = now + timedelta(days=int(day))

            job = {
                "id": f"job_{len(db['jobs'])+1}",
                "type": "followup",
                "workflow": workflow_name,
                "campaign_id": campaign_id,
                "lead_id": lead["id"],
                "channel": lead.get("channel", "email"),
                "day": int(day),
                "due_at": due.isoformat(),
                "status": "queued"
            }

            db["jobs"].append(job)
            added += 1

    _save(db)
    return {"status": "ok", "campaign_id": campaign_id, "added": added}

def run_due():
    db = _load()
    now = _now_utc()

    queued = 0
    due = 0
    sent = 0

    for job in db["jobs"]:
        if job.get("status") == "queued":
            queued += 1
            due_at = datetime.fromisoformat(job["due_at"])
            if due_at <= now:
                due += 1
                job["status"] = "sent"
                job["sent_at"] = now.isoformat()
                sent += 1

    _save(db)
    return {"status": "ok", "queued": queued, "due": due, "sent": sent}

def force_all_due():
    db = _load()
    now = _now_utc()
    for job in db["jobs"]:
        if job.get("status") == "queued":
            job["due_at"] = (now - timedelta(seconds=1)).isoformat()
    _save(db)

def reset_sent_to_queued():
    db = _load()
    for job in db["jobs"]:
        if job.get("status") == "sent":
            job["status"] = "queued"
            job.pop("sent_at", None)
    _save(db)
