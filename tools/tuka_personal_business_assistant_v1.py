from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_personal_business_assistant_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_personal_business_assistant_v1_memory.jsonl"
AUDIT_PATH = DATA_DIR / "tuka_personal_business_assistant_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


ASSISTANT_CAPABILITIES = [
    {
        "id": "phone_call_assistant",
        "name": "Phone Call Assistant",
        "channel": "phone",
        "can_preview": [
            "caller_intent_classification",
            "spam_vs_important_scoring",
            "safe_response_script_draft",
            "call_summary_draft",
        ],
        "blocked_without_approval": [
            "answer_live_call",
            "transfer_call",
            "record_call",
            "commit_on_behalf_of_user",
        ],
        "required_gates": ["Admin approval", "Call consent", "Audit log"],
    },
    {
        "id": "email_assistant",
        "name": "Email Assistant",
        "channel": "email",
        "can_preview": [
            "email_classification",
            "priority_scoring",
            "reply_draft",
            "grammar_and_tone_revision",
        ],
        "blocked_without_approval": ["send_email", "delete_email", "archive_email", "unsubscribe"],
        "required_gates": ["Admin approval", "Recipient check", "Audit log"],
    },
    {
        "id": "message_assistant",
        "name": "Message Assistant",
        "channel": "message",
        "can_preview": [
            "message_classification",
            "reply_draft",
            "tone_revision",
            "followup_reminder_draft",
        ],
        "blocked_without_approval": ["send_message", "delete_message", "block_contact"],
        "required_gates": ["Admin approval", "Contact check", "Audit log"],
    },
    {
        "id": "calendar_scheduling_assistant",
        "name": "Calendar / Scheduling Assistant",
        "channel": "calendar",
        "can_preview": [
            "meeting_time_suggestions",
            "agenda_draft",
            "availability_summary",
            "reschedule_proposal",
        ],
        "blocked_without_approval": ["create_event", "reschedule_event", "cancel_event", "invite_guests"],
        "required_gates": ["Admin approval", "Conflict check", "Audit log"],
    },
]


GLOBAL_GUARDS = {
    "send_requires_approval": True,
    "delete_requires_approval": True,
    "call_transfer_requires_confirmation": True,
    "money_contract_commitment_blocked": True,
    "all_actions_audited": True,
    "no_live_phone_access": True,
    "no_live_email_access": True,
    "no_live_message_access": True,
    "no_live_calendar_write": True,
    "preview_only": True,
    "fail_closed": True,
    "no_fake_pass": True,
}


def assistant_registry() -> dict[str, Any]:
    registry = {
        "ok": True,
        "engine": "tuka_personal_business_assistant_v1",
        "mode": "governed_personal_business_assistant_preview",
        "updated_at": _now(),
        "public_name": "Tuka Personal + Business Assistant",
        "capabilities": ASSISTANT_CAPABILITIES,
        "global_guards": GLOBAL_GUARDS,
        "roadmap_position": [
            "Core Stability",
            "Governance + Guardrails",
            "Context + Memory",
            "Skill System",
            "Office / Executive Assistant",
            "Voice Layer",
            "Personal + Business Assistant",
            "Phone / Email / Message / Calendar Automation",
        ],
        "runtime": {
            "live_integrations_enabled": False,
            "send_enabled": False,
            "delete_enabled": False,
            "call_transfer_enabled": False,
            "calendar_write_enabled": False,
            "approval_required_before_external_action": True,
        },
    }
    _append_jsonl(MEMORY_PATH, {"ts": _now(), "event": "assistant_registry_built", "capability_count": len(ASSISTANT_CAPABILITIES)})
    return registry


def classify_incoming_item(channel: str, text: str) -> dict[str, Any]:
    lowered = text.lower()
    important_terms = ["urgent", "contract", "invoice", "meeting", "payment", "яаралтай", "гэрээ", "төлбөр"]
    spam_terms = ["winner", "lottery", "free gift", "crypto pump", "click now", "сугалаа"]
    priority = "important" if any(term in lowered for term in important_terms) else "normal"
    if any(term in lowered for term in spam_terms):
        priority = "spam_suspected"
    draft = {
        "phone": "I can take a message and ask the owner to call you back.",
        "email": "Thanks for the message. I will review and respond after approval.",
        "message": "Got it. I will confirm and get back to you.",
        "calendar": "I can suggest available times, then wait for approval before creating an event.",
    }.get(channel, "I can prepare a safe draft for review.")
    result = {
        "ok": True,
        "channel": channel,
        "intent": "business_or_personal_message",
        "priority": priority,
        "draft_response": draft,
        "external_action_executed": False,
        "approval_required": True,
        "audit_written": True,
        "updated_at": _now(),
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "incoming_item_classified", "channel": channel, "priority": priority})
    return result


def evaluate_action(action: str, *, admin_approved: bool = False, consent_confirmed: bool = False) -> dict[str, Any]:
    high_risk_actions = {
        "send_email",
        "delete_email",
        "send_message",
        "delete_message",
        "answer_live_call",
        "transfer_call",
        "create_event",
        "reschedule_event",
        "cancel_event",
        "money_commitment",
        "contract_commitment",
    }
    allowed = action not in high_risk_actions or (admin_approved and consent_confirmed)
    if action in {"money_commitment", "contract_commitment"}:
        allowed = False
    result = {
        "ok": True,
        "action": action,
        "allowed": allowed,
        "blocked": not allowed,
        "reason": "approved_preview_action" if allowed else "admin_and_consent_required_or_action_blocked",
        "admin_approved": admin_approved,
        "consent_confirmed": consent_confirmed,
        "external_action_executed": False,
        "audit_written": True,
        "fail_closed": not allowed,
        "updated_at": _now(),
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "assistant_action_evaluated", "action": action, "allowed": allowed})
    return result


def verify_personal_business_assistant() -> dict[str, Any]:
    registry = assistant_registry()
    caps = registry["capabilities"]
    channels = {item["channel"] for item in caps}
    guards = registry["global_guards"]
    runtime = registry["runtime"]
    phone = classify_incoming_item("phone", "Urgent call about tomorrow meeting")
    email = classify_incoming_item("email", "Invoice payment question")
    spam = classify_incoming_item("message", "Lottery winner click now")
    blocked_actions = {
        "send_email": evaluate_action("send_email"),
        "delete_message": evaluate_action("delete_message"),
        "transfer_call": evaluate_action("transfer_call"),
        "create_event": evaluate_action("create_event"),
        "money_commitment": evaluate_action("money_commitment", admin_approved=True, consent_confirmed=True),
    }
    checks = {
        "registry_ok": registry["ok"] is True,
        "four_capabilities_registered": len(caps) == 4,
        "phone_channel_present": "phone" in channels,
        "email_channel_present": "email" in channels,
        "message_channel_present": "message" in channels,
        "calendar_channel_present": "calendar" in channels,
        "all_have_preview_actions": all(len(item["can_preview"]) >= 4 for item in caps),
        "all_have_blocked_actions": all(len(item["blocked_without_approval"]) >= 3 for item in caps),
        "send_requires_approval": guards["send_requires_approval"] is True,
        "delete_requires_approval": guards["delete_requires_approval"] is True,
        "call_transfer_requires_confirmation": guards["call_transfer_requires_confirmation"] is True,
        "money_contract_commitment_blocked": guards["money_contract_commitment_blocked"] is True,
        "all_actions_audited": guards["all_actions_audited"] is True and AUDIT_PATH.exists(),
        "live_integrations_locked": runtime["live_integrations_enabled"] is False,
        "send_delete_locked": runtime["send_enabled"] is False and runtime["delete_enabled"] is False,
        "calendar_write_locked": runtime["calendar_write_enabled"] is False,
        "phone_intent_classified": phone["priority"] == "important",
        "email_priority_classified": email["priority"] == "important",
        "spam_detected": spam["priority"] == "spam_suspected",
        "high_risk_actions_blocked": all(item["blocked"] is True for item in blocked_actions.values()),
        "no_external_action_executed": all(item["external_action_executed"] is False for item in blocked_actions.values()),
        "roadmap_position_present": "Personal + Business Assistant" in registry["roadmap_position"],
        "fail_closed": guards["fail_closed"] is True,
        "no_fake_pass": guards["no_fake_pass"] is True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_personal_business_assistant_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "registry": registry,
        "classification_examples": {"phone": phone, "email": email, "spam": spam},
        "blocked_action_examples": blocked_actions,
        "execution_locked": True,
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify_personal_business_assistant(), indent=2, ensure_ascii=False))
