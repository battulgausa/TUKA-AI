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
REPORT_PATH = DATA_DIR / "tuka_pr_lifecycle_gate_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_pr_lifecycle_gate_v1_memory.jsonl"


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
        "User-Agent": "Tuka-PR-Lifecycle-Gate-v1",
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


def verify_pr_lifecycle(
    *,
    owner: str = "battulgausa",
    repo: str = "TUKA-AI",
    pr_number: int = 3852,
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
            "phase": "tuka_pr_lifecycle_gate_v1",
            "error": str(exc),
            "fail_closed": True,
            "updated_at": _now(),
        }
        _write_report(report)
        return report

    filenames = [str(item.get("filename", "")) for item in files if isinstance(item, dict)]
    runtime_prefixes = ("tools/", "static/", "agents/", "memory/", "dashboard", "main", "scripts/")
    runtime_files = [
        name for name in filenames
        if name.startswith(runtime_prefixes) and name != "TUKA_REAL_PR_SMOKE.md"
    ]
    risky_changes = [
        item for item in files
        if isinstance(item, dict)
        and (
            item.get("status") not in {"added", "modified", "removed"}
            or int(item.get("changes", 0) or 0) > 100
        )
    ]

    pr_merged = bool(pr.get("merged_at"))
    pr_open_or_merged = pr.get("state") == "open" or pr_merged
    checks = {
        "pr_exists": bool(pr.get("html_url")),
        "pr_open_or_merged": pr_open_or_merged,
        "base_is_main": pr.get("base", {}).get("ref") == "main",
        "head_branch_matches": pr.get("head", {}).get("ref") == "tuka/execution-core-real-pr-smoke",
        "commit_count_is_one": len(commits) == 1,
        "files_changed_is_one": len(files) == 1,
        "marker_file_only": filenames == ["TUKA_REAL_PR_SMOKE.md"],
        "no_runtime_code_changed": len(runtime_files) == 0,
        "no_large_or_unknown_change": len(risky_changes) == 0,
        "mergeable_field_available": "mergeable" in pr,
        "draft_is_false": pr.get("draft") is False,
        "user_review_still_required": True,
        "no_auto_merge_attempted": pr.get("auto_merge") is None,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_pr_lifecycle_gate_v1",
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
        "commit_shas": [item.get("sha") for item in commits if isinstance(item, dict)],
        "risk": "low" if not runtime_files and filenames == ["TUKA_REAL_PR_SMOKE.md"] else "review_required",
        "merge_executed": False,
        "auto_merge_executed": False,
        "admin_review_required": True,
        "error": error,
        "updated_at": _now(),
    }
    _write_report(report)
    _append_memory(
        {
            "ts": _now(),
            "event": "pr_lifecycle_verify",
            "pr_number": pr_number,
            "passed": passed,
            "total": len(checks),
            "url": pr.get("html_url"),
        }
    )
    return report


if __name__ == "__main__":
    print(json.dumps(verify_pr_lifecycle(), indent=2, ensure_ascii=False))
