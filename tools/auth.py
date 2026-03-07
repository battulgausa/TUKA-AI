import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any

import bcrypt

USERS_DB = Path("data/users.json")
SESSIONS_DB = Path("data/sessions.json")

# Simple HMAC token (no external deps). Not JWT, but fine for prototype.
_SECRET = os.environ.get("TUKA_SECRET", "CHANGE_ME_DEV_SECRET").encode("utf-8")

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _save_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
def _load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))
def load_users() -> Dict[str, Any]:
    return _load_json(USERS_DB, {"users": [], "settings": {}})

def load_sessions() -> Dict[str, Any]:
    return _load_json(SESSIONS_DB, {"sessions": [], "revoked_tokens": []})

def save_sessions(db: Dict[str, Any]):
    _save_json(SESSIONS_DB, db)

def find_user(username: str) -> Optional[Dict[str, Any]]:
    db = load_users()
    for u in db.get("users", []):
        if u.get("username") == username:
            return u
    return None

def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False

def _sign(payload_b64: bytes) -> str:
    sig = hmac.new(_SECRET, payload_b64, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")

def issue_token(user_id: str, role: str, minutes: int = 240) -> str:
    exp = _now_utc() + timedelta(minutes=minutes)
    payload = {
        "uid": user_id,
        "role": role,
        "exp": int(exp.timestamp())
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    sig = _sign(payload_b64.encode("utf-8"))
    token = f"{payload_b64}.{sig}"

    sdb = load_sessions()
    sdb["sessions"].append({
        "token": token,
        "uid": user_id,
        "role": role,
        "exp": payload["exp"],
        "created_at": _now_utc().isoformat()
    })
    save_sessions(sdb)
    return token

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload_b64, sig = token.split(".", 1)
        expected = _sign(payload_b64.encode("utf-8"))
        if not hmac.compare_digest(sig, expected):
            return None
        # restore padding
        pad = "=" * ((4 - (len(payload_b64) % 4)) % 4)
        payload_bytes = base64.urlsafe_b64decode((payload_b64 + pad).encode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))
        return payload
    except Exception:
        return None

def is_token_revoked(token: str) -> bool:
    sdb = load_sessions()
    return token in set(sdb.get("revoked_tokens", []))

def revoke_token(token: str) -> Dict[str, Any]:
    sdb = load_sessions()
    if token not in sdb.get("revoked_tokens", []):
        sdb["revoked_tokens"].append(token)
    save_sessions(sdb)
    return {"status": "ok", "revoked": True}

def revoke_all() -> Dict[str, Any]:
    sdb = load_sessions()
    # revoke all existing tokens
    all_tokens = [s.get("token") for s in sdb.get("sessions", []) if s.get("token")]
    revoked = set(sdb.get("revoked_tokens", []))
    for t in all_tokens:
        revoked.add(t)
    sdb["revoked_tokens"] = list(revoked)
    save_sessions(sdb)
    return {"status": "ok", "revoked_all": True, "count": len(all_tokens)}

