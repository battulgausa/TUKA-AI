from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_merge_gate_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_merge_gate_v1_memory.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _github_token() -> str:
    env_token = os.getenv("GITHUB_TOKEN", "").strip() or os.getenv("GH_TOKEN", "").strip()
    if env_token:
        return env_token
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except Exception:
        return ""
    if proc.returncode != 0:
        return ""
    for line in proc.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    return ""


def _fetch_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Tuka-Merge-Gate-v1",
    }
    token = _github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _write_report(report: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_memory(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def evaluate_merge_gate(
    *,
    owner: str = "battulgausa",
    repo: str = "TUKA-AI",
    pr_number: int = 3852,
    admin_approved: bool = False,
    judge_approved: bool = False,
    guardrail_approved: bool = False,
) -> dict[str, Any]:
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        pr = _fetch_json(f"{base_url}/pulls/{pr_number}")
        files = _fetch_json(f"{base_url}/pulls/{pr_number}/files")
        commits = _fetch_json(f"{base_url}/pulls/{pr_number}/commits")
        error = None
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        report = {
            "ok": False,
            "phase": "tuka_merge_gate_v1",
            "error": str(exc),
            "fail_closed": True,
            "merge_allowed": False,
            "merge_executed": False,
            "updated_at": _now(),
        }
        _write_report(report)
        return report

    filenames = [str(item.get("filename", "")) for item in files if isinstance(item, dict)]
    runtime_files = [
        name for name in filenames
        if name.startswith(("tools/", "static/", "agents/", "memory/", "scripts/"))
    ]
    approvals = {
        "admin_approved": admin_approved,
        "judge_approved": judge_approved,
        "guardrail_approved": guardrail_approved,
    }
    required_approvals_ok = all(approvals.values())
    low_risk_marker = filenames == ["TUKA_REAL_PR_SMOKE.md"]
    pr_merged = bool(pr.get("merged_at"))
    pr_open_or_merged = pr.get("state") == "open" or pr_merged
    mergeable_clean = (
        pr_merged
        or (pr.get("mergeable") is True and pr.get("mergeable_state") in {"clean", "unstable", "has_hooks"})
    )
    merge_allowed = (
        pr.get("state") == "open"
        and pr.get("base", {}).get("ref") == "main"
        and mergeable_clean
        and required_approvals_ok
        and (low_risk_marker or not runtime_files)
    )

    checks = {
        "pr_exists": bool(pr.get("html_url")),
        "pr_open_or_merged": pr_open_or_merged,
        "base_is_main": pr.get("base", {}).get("ref") == "main",
        "mergeable_field_available": "mergeable" in pr,
        "mergeable_clean_or_reviewable": mergeable_clean,
        "commit_count_available": len(commits) >= 1,
        "files_available": len(files) >= 1,
        "risk_classified": True,
        "approvals_recorded": set(approvals) == {"admin_approved", "judge_approved", "guardrail_approved"},
        "merge_blocked_without_all_approvals": (not required_approvals_ok) and merge_allowed is False,
        "merge_not_executed": True,
        "auto_merge_not_executed": pr.get("auto_merge") is None,
        "fail_closed": merge_allowed is False,
        "admin_review_required": True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_merge_gate_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "pr": {
            "number": pr_number,
            "url": pr.get("html_url"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "merged": pr_merged,
            "merged_at": pr.get("merged_at"),
            "base": pr.get("base", {}).get("ref"),
            "head": pr.get("head", {}).get("ref"),
            "mergeable": pr.get("mergeable"),
            "mergeable_state": pr.get("mergeable_state"),
        },
        "files": filenames,
        "commit_count": len(commits),
        "risk": "low" if low_risk_marker else "review_required",
        "approvals": approvals,
        "required_approvals_ok": required_approvals_ok,
        "merge_allowed": merge_allowed,
        "merge_executed": False,
        "auto_merge_executed": False,
        "decision": "blocked_admin_judge_guardrail_required" if not merge_allowed else "ready_for_admin_merge",
        "error": error,
        "updated_at": _now(),
    }
    _write_report(report)
    _append_memory(
        {
            "ts": _now(),
            "event": "merge_gate_evaluated",
            "pr_number": pr_number,
            "merge_allowed": merge_allowed,
            "merge_executed": False,
            "passed": passed,
            "total": len(checks),
        }
    )
    return report


if __name__ == "__main__":
    print(json.dumps(evaluate_merge_gate(), indent=2, ensure_ascii=False))
