from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

import time
import traceback
from pydantic import BaseModel
from typing import Optional, Dict, Any

from tools.task_store import append_task, list_tasks, update_task_status, get_next_task
from tools.auth import (
    find_user, verify_password, issue_token, decode_token,
    is_token_revoked, revoke_token, revoke_all, load_users
)
from tools.policy import worker_allowed_now
from tools.services.repo_runner import run_repo_job

app = FastAPI(title="Tuka Admin/Worker API")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def dashboard():
    return FileResponse("static/dashboard.html")


@app.exception_handler(Exception)
async def dev_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(traceback.format_exc(), status_code=500)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginReq(BaseModel):
    username: str
    password: str


class TaskPayload(BaseModel):
    data: Dict[str, Any]


def _require_token(authorization: Optional[str]) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()

    if is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Token revoked")

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("exp", 0) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired")

    payload["token"] = token
    return payload


def _require_role(payload: Dict[str, Any], role: str):
    if payload.get("role") != role:
        raise HTTPException(status_code=403, detail="Forbidden")


def _get_worker_schedule():
    db = load_users()
    settings = db.get("settings", {})
    tz = settings.get("timezone", "America/Chicago")
    sched = settings.get("worker_schedule", {})
    return tz, sched.get("start", "08:00"), sched.get("end", "17:00")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
def login(req: LoginReq):
    user = find_user(req.username)
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        ok = verify_password(req.password, (user.get("password_hash") or ""))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = issue_token(user_id=user["id"], role=user["role"], minutes=240)
    return {"status": "ok", "token": token, "role": user["role"], "user_id": user["id"]}


@app.post("/auth/logout")
def logout(Authorization: Optional[str] = Header(default=None)):
    payload = _require_token(Authorization)
    return revoke_token(payload["token"])


# -------- Admin routes --------

@app.get("/admin/tasks")
def admin_list_tasks(
    Authorization: Optional[str] = Header(default=None),
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    created_by: Optional[str] = None,
):
    payload = _require_token(Authorization)
    _require_role(payload, "admin")

    items = list_tasks(limit=limit, offset=offset, status=status, created_by=created_by)
    return {"ok": True, "count": len(items), "items": items}


@app.get("/admin/users")
def admin_list_users(Authorization: Optional[str] = Header(default=None)):
    payload = _require_token(Authorization)
    _require_role(payload, "admin")

    db = load_users()
    users = []
    for u in db.get("users", []):
        x = dict(u)
        x["password_hash"] = "***"
        users.append(x)

    return {"status": "ok", "users": users}


@app.post("/admin/kill-switch")
def admin_kill_switch(Authorization: Optional[str] = Header(default=None)):
    payload = _require_token(Authorization)
    _require_role(payload, "admin")
    return revoke_all()


@app.post("/admin/tasks/{task_id}/status")
def admin_update_task_status(
    task_id: str,
    payload_in: dict,
    Authorization: Optional[str] = Header(default=None),
):
    payload = _require_token(Authorization)
    _require_role(payload, "admin")

    new_status = payload_in.get("status")
    if new_status not in {"submitted", "running", "done", "failed"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    updated = update_task_status(task_id=task_id, new_status=new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"ok": True, "item": updated}


@app.post("/admin/test-repo-runner")
def test_repo_runner(payload: dict):
    task_id = payload.get("task_id")
    repo = payload.get("repo")

    if not task_id or not repo:
        raise HTTPException(status_code=400, detail="task_id and repo are required")

    return run_repo_job(task_id, repo)


# -------- Worker routes --------

@app.get("/worker/policy")
def worker_policy(Authorization: Optional[str] = Header(default=None)):
    payload = _require_token(Authorization)
    _require_role(payload, "worker")

    tz, start, end = _get_worker_schedule()
    allowed = worker_allowed_now(tz_name=tz, start_hm=start, end_hm=end)

    return {
        "status": "ok",
        "allowed_now": allowed,
        "timezone": tz,
        "start": start,
        "end": end,
    }


@app.get("/worker/next-task")
def worker_next_task(Authorization: Optional[str] = Header(default=None)):
    payload = _require_token(Authorization)
    _require_role(payload, "worker")

    item = get_next_task()
    if not item:
        return {"ok": True, "item": None}

    return {"ok": True, "item": item}