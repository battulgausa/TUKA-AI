"""
Robust PersonaPlex model prefetch for Tuka.

Downloads the large PersonaPlex files before starting moshi.server so a network
timeout does not crash the live server startup path. No token values are printed.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
REPORT = DATA / "personaplex_prefetch_report.json"

REPO_ID = "nvidia/personaplex-7b-v1"
FILES = [
    "config.json",
    "voices.tgz",
    "dist.tgz",
    "tokenizer-e351c8d8-checkpoint125.safetensors",
    "tokenizer_spm_32k_3.model",
    "model.safetensors",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_present(name: str) -> bool:
    value = os.environ.get(name)
    if value:
        return True
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value, _ = winreg.QueryValueEx(key, name)
                if value:
                    os.environ[name] = value
                    return True
        except Exception:
            return False
    return False


def prefetch(max_attempts: int = 8, sleep_seconds: int = 20) -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "60")

    from huggingface_hub import hf_hub_download

    report: dict[str, Any] = {
        "ok": False,
        "updated_at": _now(),
        "repo_id": REPO_ID,
        "hf_token_present": _env_present("HF_TOKEN"),
        "files": {},
        "policy": {
            "no_secret_printing": True,
            "resume_download": True,
            "server_not_started": True,
        },
    }
    if not report["hf_token_present"]:
        report["reason"] = "hf_token_missing"
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    for filename in FILES:
        file_result: dict[str, Any] = {"ok": False, "attempts": 0}
        for attempt in range(1, max_attempts + 1):
            file_result["attempts"] = attempt
            try:
                path = hf_hub_download(
                    REPO_ID,
                    filename,
                    resume_download=True,
                    token=os.environ.get("HF_TOKEN"),
                )
                file_result.update(
                    {
                        "ok": True,
                        "path": path,
                        "size_bytes": Path(path).stat().st_size if Path(path).exists() else None,
                    }
                )
                break
            except Exception as exc:
                file_result["last_error_type"] = type(exc).__name__
                file_result["last_error"] = str(exc)[:700]
                if attempt < max_attempts:
                    time.sleep(sleep_seconds)
        report["files"][filename] = file_result
        report["updated_at"] = _now()
        REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        if not file_result["ok"]:
            report["reason"] = f"download_failed:{filename}"
            return report

    report["ok"] = all(item.get("ok") for item in report["files"].values())
    report["reason"] = "prefetch_complete" if report["ok"] else "prefetch_incomplete"
    report["updated_at"] = _now()
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(prefetch(), indent=2, ensure_ascii=False))
