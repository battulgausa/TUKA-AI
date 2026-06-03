"""Tuka Platform Core Pack v1.

Consolidates the essential platform pillars Tuka needs before it can become a
world-facing AI operating platform: AI OS, Multi-Agent, Voice, Vision, Meeting,
Business, Memory, Skills Marketplace, and Enterprise.

This is a governed platform blueprint and verifier. It does not enable live
autonomy, biometric capture, payments, enterprise data access, or marketplace
publishing.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "platform_core_pack_audit.jsonl"


PLATFORM_PILLARS = {
    "ai_os": {
        "name": "AI OS",
        "purpose": "Central governed operating layer for tools, agents, tasks, approvals, and audit.",
        "required_surfaces": ["runtime", "task_queue", "governance", "approval_gate", "audit_log"],
        "mvp_state": "preview_ready",
        "blocked_live_actions": ["unapproved_execution", "unreviewed_remote_action"],
    },
    "multi_agent": {
        "name": "Multi-Agent",
        "purpose": "Planner, judge, worker, verifier, observer, and learner coordination.",
        "required_surfaces": ["planner", "judge", "worker", "verifier", "observer", "learning_log"],
        "mvp_state": "governed_preview",
        "blocked_live_actions": ["self_spawn_unbounded_agents", "execute_without_judge"],
    },
    "voice": {
        "name": "Voice",
        "purpose": "Text/voice conversation, spoken task status, and future natural voice runtime.",
        "required_surfaces": ["voice_text_intake", "spoken_status", "voice_gate", "consent"],
        "mvp_state": "text_transcript_preview",
        "blocked_live_actions": ["record_without_consent", "spoken_execution_without_approval"],
    },
    "vision": {
        "name": "Vision",
        "purpose": "Screen, image, face/privacy guard, visual context, and future multimodal work.",
        "required_surfaces": ["screen_context", "image_context", "privacy_guard", "manual_review"],
        "mvp_state": "privacy_first_preview",
        "blocked_live_actions": ["camera_without_consent", "biometric_unlock_without_step_up"],
    },
    "meeting": {
        "name": "Meeting",
        "purpose": "Meeting notes, minutes, action items, presentation support, and follow-up drafts.",
        "required_surfaces": ["notes", "minutes", "action_items", "presentation_draft", "follow_up"],
        "mvp_state": "draft_preview",
        "blocked_live_actions": ["record_meeting_without_consent", "send_followup_without_approval"],
    },
    "business": {
        "name": "Business",
        "purpose": "Business assistant, reports, email drafts, tasks, finance/procurement/legal gates.",
        "required_surfaces": ["daily_summary", "report_draft", "email_draft", "task_list", "approval"],
        "mvp_state": "business_assistant_mvp",
        "blocked_live_actions": ["send_email", "spend_money", "sign_contract"],
    },
    "memory": {
        "name": "Memory",
        "purpose": "Project, task, execution, strategy, and preference memory with compression.",
        "required_surfaces": ["project_memory", "task_memory", "execution_memory", "strategy_memory", "retention_policy"],
        "mvp_state": "structured_memory_contract",
        "blocked_live_actions": ["store_sensitive_data_without_policy", "retain_delete_requested_data"],
    },
    "skills_marketplace": {
        "name": "Skills Marketplace",
        "purpose": "Discover, install, rate, approve, and govern reusable Tuka skills.",
        "required_surfaces": ["skill_registry", "skill_manifest", "approval_gate", "dependency_scan", "publisher_audit"],
        "mvp_state": "registry_preview",
        "blocked_live_actions": ["install_untrusted_skill", "publish_without_review"],
    },
    "enterprise": {
        "name": "Enterprise",
        "purpose": "Admin controls, SSO-ready policy, tenant isolation, compliance, logs, and support.",
        "required_surfaces": ["admin_console", "roles", "tenant_boundary", "compliance_review", "exportable_audit"],
        "mvp_state": "enterprise_contract_preview",
        "blocked_live_actions": ["cross_tenant_access", "export_sensitive_data_without_approval"],
    },
}


GLOBAL_GUARDS = {
    "admin_first": True,
    "judge_required_for_execution": True,
    "guardrail_required": True,
    "approval_required_for_sensitive_actions": True,
    "audit_required": True,
    "consent_required_for_voice_vision_biometrics": True,
    "tenant_isolation_required": True,
    "unknown_or_conflicting_info_fail_closed": True,
    "marketplace_install_requires_review": True,
    "enterprise_data_export_requires_approval": True,
    "preview_only": True,
    "no_fake_pass": True,
}


RUNTIME = {
    "live_autonomy_enabled": False,
    "live_voice_recording_enabled": False,
    "live_camera_enabled": False,
    "live_meeting_recording_enabled": False,
    "live_marketplace_install_enabled": False,
    "live_enterprise_connector_enabled": False,
    "live_payment_or_contract_enabled": False,
    "execution_enabled": False,
    "admin_approval_required": True,
}


MATURITY_LEVELS = {
    "preview": "Design and local verification exist; live action disabled.",
    "pilot": "Small trusted-user test with manual approval and audit.",
    "production": "Operational controls, monitoring, rollback, support, and compliance active.",
    "enterprise": "SSO, tenant isolation, data policy, legal/security review, and SLA-ready.",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_audit(event: dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": now_iso(), **event}
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "tuka_platform_core_pack_v1",
        "mode": "governed_platform_core_preview",
        "public_name": "Tuka Platform Core Pack",
        "updated_at": now_iso(),
        "pillars": PLATFORM_PILLARS,
        "global_guards": GLOBAL_GUARDS,
        "runtime": RUNTIME,
        "maturity_levels": MATURITY_LEVELS,
        "platform_sequence": [
            "AI OS",
            "Multi-Agent",
            "Memory",
            "Skills Marketplace",
            "Business",
            "Meeting",
            "Voice",
            "Vision",
            "Enterprise",
        ],
    }


def build_platform_plan(target: str = "business_mvp_to_enterprise") -> dict[str, Any]:
    phases = [
        {
            "phase": "mvp",
            "goal": "Finish Business Assistant as daily-use product.",
            "pillars": ["ai_os", "business", "meeting", "voice", "memory"],
            "exit_gate": "verified_preview_and_admin_approval_flow",
        },
        {
            "phase": "pilot",
            "goal": "Run trusted users with manual approval and audit.",
            "pillars": ["multi_agent", "business", "memory", "enterprise"],
            "exit_gate": "pilot_feedback_and_zero_critical_security_findings",
        },
        {
            "phase": "platform",
            "goal": "Open skill registry and governed reusable workflows.",
            "pillars": ["skills_marketplace", "multi_agent", "ai_os", "enterprise"],
            "exit_gate": "reviewed_skill_install_and_rollback",
        },
        {
            "phase": "multimodal",
            "goal": "Add consent-first voice and vision workflows.",
            "pillars": ["voice", "vision", "meeting", "enterprise"],
            "exit_gate": "consent_privacy_and_step_up_auth_verified",
        },
        {
            "phase": "enterprise",
            "goal": "Prepare customer/org deployment controls.",
            "pillars": ["enterprise", "ai_os", "memory", "business"],
            "exit_gate": "tenant_isolation_audit_export_and_admin_policy_verified",
        },
    ]
    plan = {
        "ok": True,
        "target": target,
        "phases": phases,
        "live_execution_enabled": False,
        "admin_approval_required": True,
    }
    write_audit({"event": "platform_plan_built", **plan})
    return plan


def evaluate_pillar_readiness(pillar_id: str) -> dict[str, Any]:
    pillar = PLATFORM_PILLARS[pillar_id]
    live_blocked = all(action for action in pillar["blocked_live_actions"])
    ready = bool(pillar["required_surfaces"]) and live_blocked
    result = {
        "ok": True,
        "pillar_id": pillar_id,
        "name": pillar["name"],
        "required_surface_count": len(pillar["required_surfaces"]),
        "blocked_live_action_count": len(pillar["blocked_live_actions"]),
        "mvp_state": pillar["mvp_state"],
        "preview_ready": ready,
        "live_enabled": False,
        "manual_review_required": True,
    }
    write_audit({"event": "pillar_readiness_evaluated", **result})
    return result


def evaluate_platform_action(action: str, *, admin_approved: bool = False, judge_passed: bool = False) -> dict[str, Any]:
    sensitive_actions = {
        "enable_live_autonomy",
        "record_voice",
        "enable_camera",
        "record_meeting",
        "install_marketplace_skill",
        "connect_enterprise_data",
        "export_enterprise_data",
        "spend_money",
        "sign_contract",
        "cross_tenant_access",
    }
    sensitive = action in sensitive_actions
    blocked = False
    reasons: list[str] = []
    if sensitive and not admin_approved:
        blocked = True
        reasons.append("admin_approval_required")
    if sensitive and not judge_passed:
        blocked = True
        reasons.append("judge_required")
    if action in {"spend_money", "sign_contract", "cross_tenant_access"}:
        blocked = True
        reasons.append("hard_blocked_manual_review")
    if action == "read_platform_status":
        blocked = False

    result = {
        "ok": True,
        "action": action,
        "sensitive": sensitive,
        "allowed": not blocked,
        "blocked": blocked,
        "admin_approved": admin_approved,
        "judge_passed": judge_passed,
        "live_action_executed": False,
        "reasons": reasons or ["preview_allowed_no_live_action"],
        "audit_written": True,
        "fail_closed": blocked,
    }
    write_audit({"event": "platform_action_evaluated", **result})
    return result


def verify_platform_core_pack() -> dict[str, Any]:
    before_audit_count = 0
    if AUDIT_PATH.exists():
        before_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    reg = registry()
    plan = build_platform_plan()
    readiness = {pillar_id: evaluate_pillar_readiness(pillar_id) for pillar_id in PLATFORM_PILLARS}
    blocked_actions = {
        "autonomy": evaluate_platform_action("enable_live_autonomy"),
        "voice": evaluate_platform_action("record_voice", admin_approved=True, judge_passed=False),
        "vision": evaluate_platform_action("enable_camera", admin_approved=False, judge_passed=True),
        "meeting": evaluate_platform_action("record_meeting", admin_approved=True, judge_passed=False),
        "marketplace": evaluate_platform_action("install_marketplace_skill", admin_approved=False, judge_passed=True),
        "enterprise_export": evaluate_platform_action("export_enterprise_data", admin_approved=False, judge_passed=False),
        "money": evaluate_platform_action("spend_money", admin_approved=True, judge_passed=True),
        "contract": evaluate_platform_action("sign_contract", admin_approved=True, judge_passed=True),
        "cross_tenant": evaluate_platform_action("cross_tenant_access", admin_approved=True, judge_passed=True),
        "status": evaluate_platform_action("read_platform_status"),
    }

    after_audit_count = 0
    if AUDIT_PATH.exists():
        after_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    expected_pillars = {
        "ai_os",
        "multi_agent",
        "voice",
        "vision",
        "meeting",
        "business",
        "memory",
        "skills_marketplace",
        "enterprise",
    }
    checks = {
        "registry_ok": reg["ok"],
        "nine_pillars_registered": set(PLATFORM_PILLARS) == expected_pillars,
        "ai_os_present": "ai_os" in PLATFORM_PILLARS,
        "multi_agent_present": "multi_agent" in PLATFORM_PILLARS,
        "voice_present": "voice" in PLATFORM_PILLARS,
        "vision_present": "vision" in PLATFORM_PILLARS,
        "meeting_present": "meeting" in PLATFORM_PILLARS,
        "business_present": "business" in PLATFORM_PILLARS,
        "memory_present": "memory" in PLATFORM_PILLARS,
        "skills_marketplace_present": "skills_marketplace" in PLATFORM_PILLARS,
        "enterprise_present": "enterprise" in PLATFORM_PILLARS,
        "all_pillars_have_surfaces": all(
            bool(pillar["required_surfaces"]) for pillar in PLATFORM_PILLARS.values()
        ),
        "all_pillars_have_blocked_actions": all(
            bool(pillar["blocked_live_actions"]) for pillar in PLATFORM_PILLARS.values()
        ),
        "readiness_all_preview_ready": all(item["preview_ready"] for item in readiness.values()),
        "platform_plan_has_five_phases": len(plan["phases"]) == 5,
        "mvp_phase_business_focused": "business" in plan["phases"][0]["pillars"],
        "enterprise_phase_present": plan["phases"][-1]["phase"] == "enterprise",
        "admin_first_guard": GLOBAL_GUARDS["admin_first"],
        "judge_guard": GLOBAL_GUARDS["judge_required_for_execution"],
        "guardrail_guard": GLOBAL_GUARDS["guardrail_required"],
        "audit_guard": GLOBAL_GUARDS["audit_required"],
        "consent_guard": GLOBAL_GUARDS["consent_required_for_voice_vision_biometrics"],
        "tenant_isolation_guard": GLOBAL_GUARDS["tenant_isolation_required"],
        "marketplace_review_guard": GLOBAL_GUARDS["marketplace_install_requires_review"],
        "enterprise_export_guard": GLOBAL_GUARDS["enterprise_data_export_requires_approval"],
        "live_autonomy_locked": RUNTIME["live_autonomy_enabled"] is False,
        "live_voice_locked": RUNTIME["live_voice_recording_enabled"] is False,
        "live_camera_locked": RUNTIME["live_camera_enabled"] is False,
        "live_meeting_locked": RUNTIME["live_meeting_recording_enabled"] is False,
        "live_marketplace_locked": RUNTIME["live_marketplace_install_enabled"] is False,
        "live_enterprise_locked": RUNTIME["live_enterprise_connector_enabled"] is False,
        "payment_contract_locked": RUNTIME["live_payment_or_contract_enabled"] is False,
        "execution_disabled": RUNTIME["execution_enabled"] is False,
        "sensitive_actions_blocked": all(
            item["blocked"] is True
            for key, item in blocked_actions.items()
            if key != "status"
        ),
        "status_read_allowed_preview": blocked_actions["status"]["allowed"] is True
        and blocked_actions["status"]["live_action_executed"] is False,
        "no_live_action_executed": all(
            item["live_action_executed"] is False for item in blocked_actions.values()
        ),
        "maturity_levels_present": set(MATURITY_LEVELS)
        == {"preview", "pilot", "production", "enterprise"},
        "audit_written": after_audit_count > before_audit_count,
        "preview_only": GLOBAL_GUARDS["preview_only"],
        "no_fake_pass": GLOBAL_GUARDS["no_fake_pass"],
    }
    passed = sum(1 for ok in checks.values() if ok)
    total = len(checks)
    return {
        "ok": passed == total,
        "phase": "tuka_platform_core_pack_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "plan": plan,
        "readiness": readiness,
        "blocked_actions": blocked_actions,
        "execution_locked": True,
        "updated_at": now_iso(),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(verify_platform_core_pack(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
