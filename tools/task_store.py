from __future__ import annotations

import # Tuka bugfix note: task persistence should remain deterministic 20260411-083420\n# Tuka bugfix note: task persistence should remain deterministic 20260412-184431\njson
import os
import threading
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional
from uuid import uuid4

_LOCK = threading.Lock()

DEFAULT_TASKS_PATH = os.getenv("TASKS_PATH", "data/tasks.jsonl")
DEFAULT_TZ = os.getenv("APP_TZ", "America/Chicago")

def _now_iso() -> str:
    tz = ZoneInfo(DEFAULT_TZ)
    return datetime.now(tz=tz).isoformat()

def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)

@dataclass
class TaskRecord:
    id: str
    created_at: str
    created_by: str
    status: str
    task: Dict[str, Any]

def append_task(task: Dict[str, Any], created_by: str, path: str = DEFAULT_TASKS_PATH) -> TaskRecord:
    ensure_parent_dir(path)
    record = TaskRecord(
        id=str(uuid4()),
        created_at=_now_iso(),
        created_by=created_by,
        status="submitted",
        task=task,
    )

    line = json.dumps(record.__dict__, ensure_ascii=False)

    with _LOCK:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    return record

def list_tasks(
    path: str = DEFAULT_TASKS_PATH,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    created_by: Optional[str] = None,
    newest_first: bool = True,
) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []

    with _LOCK:
        with open(path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]

    items: List[Dict[str, Any]] = []
    for ln in lines:
        try:
            items.append(json.loads(ln))
        except Exception:
            continue

    if status:
        items = [x for x in items if x.get("status") == status]
    if created_by:
        items = [x for x in items if x.get("created_by") == created_by]

    if newest_first:
        items = list(reversed(items))

    return items[offset : offset + limit]
def update_task_status(
    task_id: str,
    new_status: str,
    path: str = DEFAULT_TASKS_PATH,
) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None

    with _LOCK:
        with open(path, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]

        items: List[Dict[str, Any]] = []
        updated: Optional[Dict[str, Any]] = None

        for ln in lines:
            try:
                item = json.loads(ln)
            except Exception:
                continue

            if item.get("id") == task_id:
                item["status"] = new_status
                item["updated_at"] = _now_iso()
                updated = item

            items.append(item)

        if updated is None:
            return None

        with open(path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return updated


def get_next_task(
    path: str = DEFAULT_TASKS_PATH,
    created_by: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    items = list_tasks(path=path, limit=1000, offset=0, newest_first=False)

    for item in items:
        if item.get("status") != "submitted":
            continue
        if created_by and item.get("created_by") != created_by:
            continue
        return item

    return None
