import json
import os
from datetime import datetime

DB_PATH = os.path.join("data", "crm.json")

def _load():
    if not os.path.exists(DB_PATH):
        return {"leads": [], "workflows": [], "templates": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(db):
    os.makedirs("data", exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def create_workflow(name: str, stages: list[str]) -> dict:
    db = _load()
    wf = {
        "id": f"wf_{len(db['workflows'])+1}",
        "name": name,
        "stages": stages,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    db["workflows"].append(wf)
    _save(db)
    return wf

def add_template(kind: str, text: str) -> dict:
    db = _load()
    tpl = {
        "id": f"tpl_{len(db['templates'])+1}",
        "kind": kind,
        "text": text,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    db["templates"].append(tpl)
    _save(db)
    return tpl

def add_lead(name: str, channel: str) -> dict:
    db = _load()
    lead = {
        "id": f"lead_{len(db['leads'])+1}",
        "name": name,
        "channel": channel,
        "status": "new"
    }
    db["leads"].append(lead)
    _save(db)
    return lead

def read_db() -> dict:
    return _load()
from datetime import datetime, timezone

def update_lead_stage(lead_id: str, stage: str, contacted_at: str | None = None):
    db = read_db()
    now = contacted_at or datetime.now(timezone.utc).isoformat()

    for lead in db.get("leads", []):
        if lead.get("id") == lead_id:
            lead["stage"] = stage
            lead["last_contacted_at"] = now
            break

    write_db(db)
    return {"status": "ok", "lead_id": lead_id, "stage": stage, "at": now}

def get_lead(lead_id: str):
    db = read_db()
    for lead in db.get("leads", []):
        if lead.get("id") == lead_id:
            return lead
    return None