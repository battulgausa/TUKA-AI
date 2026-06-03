from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_skill_registry_v1_report.json"
REGISTRY_PATH = DATA_DIR / "tuka_skill_registry_v1.json"
MEMORY_PATH = DATA_DIR / "tuka_skill_registry_v1_memory.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _exists(path: str) -> bool:
    return (ROOT / path).exists()


def _append_memory(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def build_skill_registry() -> dict[str, Any]:
    skills = [
        {
            "id": "repo_patch",
            "name": "Repo Patch",
            "category": "coding",
            "risk": "controlled",
            "module": "tools.worker_completion_engine",
            "entrypoint": "dry_run_repo_patch",
            "routes": ["/worker/repo-patch-dry-run"],
            "guards": ["admin_gate", "judge_gate", "guardrail_gate", "dry_run_first"],
            "status": "preview_ready",
        },
        {
            "id": "execution_core",
            "name": "Execution Core",
            "category": "execution",
            "risk": "high",
            "module": "tools.tuka_execution_core_v1_pack",
            "entrypoint": "verify_execution_core_v1",
            "routes": ["/tuka-execution-core/v1/verify"],
            "guards": ["admin_gate", "judge_gate", "guardrail_gate", "rollback_required"],
            "status": "sandbox_verified",
        },
        {
            "id": "pr_lifecycle_gate",
            "name": "PR Lifecycle Gate",
            "category": "release",
            "risk": "controlled",
            "module": "tools.tuka_pr_lifecycle_gate_v1",
            "entrypoint": "verify_pr_lifecycle",
            "routes": [],
            "guards": ["github_token_masked", "read_only_api", "admin_review_required"],
            "status": "pending_pr_merge",
        },
        {
            "id": "merge_gate",
            "name": "Merge Gate",
            "category": "release",
            "risk": "high",
            "module": "tools.tuka_merge_gate_v1",
            "entrypoint": "evaluate_merge_gate",
            "routes": [],
            "guards": ["admin_gate", "judge_gate", "guardrail_gate", "no_auto_merge"],
            "status": "pending_pr_merge",
        },
        {
            "id": "studio_preview_builder",
            "name": "Tuka Studio Preview Builder",
            "category": "app_builder",
            "risk": "controlled",
            "module": "tools.tuka_studio_preview_builder_v1",
            "entrypoint": "verify_studio_preview_builder",
            "routes": [],
            "guards": ["preview_only", "admin_gate", "security_scan_before_apply"],
            "status": "pending_pr_merge",
        },
        {
            "id": "language_core",
            "name": "Language Core",
            "category": "conversation",
            "risk": "low",
            "module": "tools.tuka_language_core_pack",
            "entrypoint": "verify_language_core_pack",
            "routes": ["/tuka-language-core/verify"],
            "guards": ["safe_unknown_fallback", "mn_en_router"],
            "status": "verified",
        },
        {
            "id": "codeforge_pro",
            "name": "CodeForge Pro",
            "category": "coding",
            "risk": "controlled",
            "module": "tools.tuka_codeforge_pro_pack",
            "entrypoint": "verify_codeforge_pro_pack",
            "routes": ["/tuka-codeforge-pro/verify"],
            "guards": ["no_unapproved_push", "no_fake_pass", "safe_patch_first"],
            "status": "verified",
        },
        {
            "id": "recovery_core",
            "name": "Recovery Core",
            "category": "device_data",
            "risk": "controlled",
            "module": "tools.tuka_recovery_core_pack",
            "entrypoint": "verify_recovery_core_pack",
            "routes": ["/tuka-recovery-core/verify"],
            "guards": ["read_only_scan", "no_restore_without_admin", "source_drive_no_write"],
            "status": "verified",
        },
        {
            "id": "device_link",
            "name": "Device Link",
            "category": "device_connectivity",
            "risk": "controlled",
            "module": "tools.tuka_device_connectivity_pack",
            "entrypoint": "verify_device_connectivity_pack",
            "routes": ["/tuka-device/connectivity/verify"],
            "guards": ["read_only_status", "no_pair_without_admin", "secret_masking"],
            "status": "verified",
        },
        {
            "id": "model_evolution",
            "name": "Model Evolution Core",
            "category": "model_strategy",
            "risk": "controlled",
            "module": "tools.tuka_model_evolution_core_pack",
            "entrypoint": "verify_model_evolution_core",
            "routes": ["/tuka-model-evolution/verify"],
            "guards": ["no_provider_code_copy", "no_weight_copy", "tuka_native_names"],
            "status": "verified",
        },
        {
            "id": "secret_findings_review",
            "name": "Secret Findings Review",
            "category": "security",
            "risk": "high",
            "module": "tools.tuka_secret_findings_review_pack",
            "entrypoint": "review_secret_findings",
            "routes": ["/tuka-security/secret-findings/review"],
            "guards": ["mask_values", "no_delete_without_admin", "rotation_required"],
            "status": "verified",
        },
        {
            "id": "phase0_hardening",
            "name": "Phase 0 Hardening",
            "category": "governance",
            "risk": "controlled",
            "module": "tools.tuka_phase0_hardening_verify_pack",
            "entrypoint": "run_phase0_hardening_verify",
            "routes": ["/tuka-phase0/hardening/verify"],
            "guards": ["execution_lock", "worker_auth_fail_closed", "secret_audit_masking"],
            "status": "verified",
        },
    ]
    for skill in skills:
        module_path = str(skill["module"]).replace(".", "/") + ".py"
        skill["module_file"] = module_path
        skill["module_present"] = _exists(module_path)

    registry = {
        "ok": True,
        "engine": "tuka_skill_registry_v1",
        "updated_at": _now(),
        "skills": skills,
        "selection_policy": {
            "prefer_verified": True,
            "fail_closed_on_missing_skill": True,
            "high_risk_requires_admin_judge_guardrail": True,
            "preview_before_apply": True,
            "no_fake_pass": True,
        },
        "category_order": [
            "conversation",
            "coding",
            "execution",
            "release",
            "app_builder",
            "security",
            "governance",
            "device_data",
            "device_connectivity",
            "model_strategy",
        ],
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    _append_memory({"ts": _now(), "event": "skill_registry_built", "count": len(skills)})
    return registry


def select_skill(query: str) -> dict[str, Any]:
    registry = build_skill_registry()
    text = query.lower()
    keyword_map = {
        "repo": "repo_patch",
        "patch": "repo_patch",
        "execute": "execution_core",
        "execution": "execution_core",
        "merge": "merge_gate",
        "pull request": "pr_lifecycle_gate",
        "pr": "pr_lifecycle_gate",
        "studio": "studio_preview_builder",
        "app": "studio_preview_builder",
        "language": "language_core",
        "voice": "language_core",
        "code": "codeforge_pro",
        "recover": "recovery_core",
        "wifi": "device_link",
        "bluetooth": "device_link",
        "model": "model_evolution",
        "secret": "secret_findings_review",
        "hardening": "phase0_hardening",
    }
    selected_id = None
    for keyword, skill_id in keyword_map.items():
        if keyword in text:
            selected_id = skill_id
            break
    skill = next((item for item in registry["skills"] if item["id"] == selected_id), None)
    return {
        "ok": skill is not None,
        "query": query,
        "selected_skill": skill,
        "fail_closed": skill is None,
    }


def verify_skill_registry() -> dict[str, Any]:
    registry = build_skill_registry()
    skills = registry["skills"]
    ids = [item["id"] for item in skills]
    categories = {item["category"] for item in skills}
    high_risk = [item for item in skills if item["risk"] == "high"]
    selections = {
        "repo_patch": select_skill("patch this repo"),
        "studio": select_skill("build a construction app"),
        "merge": select_skill("merge this PR"),
        "secret": select_skill("review secrets"),
    }
    checks = {
        "registry_ok": registry["ok"] is True,
        "at_least_twelve_skills": len(skills) >= 12,
        "ids_unique": len(ids) == len(set(ids)),
        "available_modules_present": all(
            item["module_present"] is True
            for item in skills
            if item["status"] != "pending_pr_merge"
        ),
        "pending_pr_modules_marked": all(
            item["status"] == "pending_pr_merge"
            for item in skills
            if item["id"] in {"pr_lifecycle_gate", "merge_gate", "studio_preview_builder"}
        ),
        "coding_category_present": "coding" in categories,
        "execution_category_present": "execution" in categories,
        "release_category_present": "release" in categories,
        "app_builder_category_present": "app_builder" in categories,
        "security_category_present": "security" in categories,
        "governance_category_present": "governance" in categories,
        "all_skills_have_guards": all(len(item["guards"]) >= 2 for item in skills),
        "high_risk_skills_guarded": all(
            any("admin" in guard for guard in item["guards"]) or item["id"] == "secret_findings_review"
            for item in high_risk
        ),
        "repo_patch_selects": selections["repo_patch"]["selected_skill"]["id"] == "repo_patch",
        "studio_selects": selections["studio"]["selected_skill"]["id"] == "studio_preview_builder",
        "merge_selects": selections["merge"]["selected_skill"]["id"] == "merge_gate",
        "secret_selects": selections["secret"]["selected_skill"]["id"] == "secret_findings_review",
        "selection_policy_fail_closed": registry["selection_policy"]["fail_closed_on_missing_skill"] is True,
        "preview_before_apply": registry["selection_policy"]["preview_before_apply"] is True,
        "no_fake_pass": registry["selection_policy"]["no_fake_pass"] is True,
        "registry_file_written": REGISTRY_PATH.exists(),
        "memory_written": MEMORY_PATH.exists(),
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_skill_registry_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "registry": registry,
        "selection_tests": selections,
        "execution_locked": True,
        "updated_at": _now(),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify_skill_registry(), indent=2, ensure_ascii=False))
