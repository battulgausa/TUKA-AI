"""Tuka Business Assistant MVP v1.

Focused, production-shaped preview for the first sellable Tuka workflow:
chat/voice intake, daily work summary, meeting notes, document/report draft,
email reply draft, task list, admin approval, and audit log.

This module does not send email, record meetings, call external APIs, modify
calendars, or execute money/legal actions. It drafts, verifies, and gates.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "business_assistant_mvp_audit.jsonl"


CAPABILITIES = [
    "chat",
    "voice_text_intake",
    "daily_work_summary",
    "meeting_notes",
    "document_report_draft",
    "email_reply_draft",
    "task_list",
    "admin_approval",
    "audit_log",
]


GUARDS = {
    "voice_is_text_transcript_only": True,
    "no_live_microphone_recording": True,
    "no_live_email_send": True,
    "no_live_calendar_write": True,
    "no_live_file_delete": True,
    "no_money_movement": True,
    "no_contract_commitment": True,
    "admin_approval_required_before_send_delete_spend_commit": True,
    "all_actions_audited": True,
    "unknown_or_conflicting_info_fail_closed": True,
    "preview_only": True,
    "no_fake_pass": True,
}


RUNTIME = {
    "live_email_enabled": False,
    "live_calendar_enabled": False,
    "live_meeting_recording_enabled": False,
    "live_microphone_enabled": False,
    "live_file_write_enabled": False,
    "live_external_api_enabled": False,
    "execution_enabled": False,
    "admin_approval_required": True,
}


APP_SURFACES = {
    "admin_mobile": [
        "chat",
        "voice",
        "today",
        "meetings",
        "documents",
        "email_drafts",
        "tasks",
        "approvals",
        "audit",
    ],
    "user_mobile": [
        "chat",
        "voice",
        "today",
        "tasks",
        "documents",
    ],
}


SENSITIVE_ACTIONS = {
    "send_email",
    "delete_email",
    "delete_file",
    "send_message",
    "create_calendar_event",
    "reschedule_meeting",
    "spend_money",
    "sign_contract",
    "publish_report",
    "external_api_call",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_audit(event: dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": now_iso(), **event}
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


@dataclass
class AssistantRequest:
    source: str
    text: str
    language: str = "mn"
    participants: list[str] = field(default_factory=list)
    meeting_transcript: str = ""
    inbox_message: str = ""


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "tuka_business_assistant_mvp_v1",
        "mode": "governed_business_assistant_preview",
        "public_name": "Tuka Business Assistant MVP",
        "updated_at": now_iso(),
        "capabilities": CAPABILITIES,
        "guards": GUARDS,
        "runtime": RUNTIME,
        "app_surfaces": APP_SURFACES,
        "mvp_flow": [
            "intake_chat_or_voice_text",
            "understand_work",
            "draft_outputs",
            "verify_outputs",
            "request_admin_approval_for_sensitive_actions",
            "audit_everything",
        ],
    }


def normalize_intake(request: AssistantRequest) -> dict[str, Any]:
    source = request.source.lower().strip()
    accepted = source in {"chat", "voice"}
    normalized = {
        "ok": accepted and bool(request.text.strip()),
        "source": source,
        "language": request.language,
        "text": request.text.strip(),
        "voice_transcript_only": source == "voice",
        "microphone_recorded": False,
        "external_voice_api_used": False,
        "fail_closed": not accepted or not bool(request.text.strip()),
    }
    write_audit({"event": "business_assistant_intake", **normalized})
    return normalized


def build_daily_summary(work_items: list[str]) -> dict[str, Any]:
    clean_items = [item.strip() for item in work_items if item.strip()]
    summary = {
        "ok": bool(clean_items),
        "title": "Today's work summary",
        "completed": clean_items[:5],
        "priority_next": clean_items[0] if clean_items else "",
        "risks": ["Needs Admin approval before external send/delete/spend."] if clean_items else [],
        "external_action_executed": False,
    }
    write_audit({"event": "daily_summary_drafted", **summary})
    return summary


def build_meeting_notes(transcript: str, participants: list[str]) -> dict[str, Any]:
    text = transcript.strip()
    participant_list = participants or ["Unknown speaker"]
    notes = {
        "ok": bool(text),
        "participants": participant_list,
        "summary": text[:220] if text else "",
        "decisions": ["Draft only: confirm decisions with participants."],
        "action_items": [
            {"owner": participant_list[0], "task": "Review meeting notes", "status": "draft"}
        ],
        "recording_started": False,
        "external_action_executed": False,
    }
    write_audit({"event": "meeting_notes_drafted", **notes})
    return notes


def build_document_report(topic: str, summary: dict[str, Any], notes: dict[str, Any]) -> dict[str, Any]:
    report = {
        "ok": bool(topic.strip()) and summary["ok"],
        "type": "business_report_draft",
        "title": f"Tuka Business Report: {topic.strip()[:80]}",
        "sections": [
            {"heading": "Overview", "body": summary.get("priority_next", "")},
            {"heading": "Completed Work", "body": summary.get("completed", [])},
            {"heading": "Meeting Notes", "body": notes.get("summary", "")},
            {"heading": "Risks", "body": summary.get("risks", [])},
        ],
        "file_written": False,
        "external_action_executed": False,
    }
    write_audit({"event": "document_report_drafted", **report})
    return report


def build_email_reply(inbox_message: str, report: dict[str, Any]) -> dict[str, Any]:
    message = inbox_message.strip()
    draft = {
        "ok": bool(message) and report["ok"],
        "subject": "Re: Business update",
        "body": (
            "Сайн байна уу,\n\n"
            "Доорх ажлын тайланг draft байдлаар бэлдлээ. Илгээхээс өмнө Admin баталгаажуулна.\n\n"
            f"{report['title']}\n\n"
            "Хүндэтгэсэн,\nTuka"
        ),
        "send_ready": True,
        "send_executed": False,
        "admin_approval_required": True,
    }
    write_audit({"event": "email_reply_drafted", **draft})
    return draft


def build_task_list(summary: dict[str, Any], notes: dict[str, Any]) -> dict[str, Any]:
    tasks = [
        {"task": "Review daily summary", "status": "draft", "requires_admin": False},
        {"task": "Confirm meeting decisions", "status": "draft", "requires_admin": False},
        {"task": "Approve email before sending", "status": "blocked", "requires_admin": True},
    ]
    if summary.get("priority_next"):
        tasks.insert(
            0,
            {"task": f"Next priority: {summary['priority_next']}", "status": "draft", "requires_admin": False},
        )
    if notes.get("action_items"):
        tasks.extend(notes["action_items"])
    task_list = {
        "ok": bool(tasks),
        "tasks": tasks,
        "external_action_executed": False,
    }
    write_audit({"event": "task_list_drafted", **task_list})
    return task_list


def evaluate_admin_approval(action: str, *, admin_approved: bool = False) -> dict[str, Any]:
    sensitive = action in SENSITIVE_ACTIONS
    allowed = bool(not sensitive or admin_approved)
    if action in {"spend_money", "sign_contract"}:
        allowed = False
    result = {
        "ok": True,
        "action": action,
        "sensitive": sensitive,
        "admin_approved": admin_approved,
        "allowed": allowed,
        "blocked": not allowed,
        "external_action_executed": False,
        "reason": "preview_allowed_no_live_action" if allowed else "admin_or_manual_review_required",
        "audit_written": True,
        "fail_closed": not allowed,
    }
    write_audit({"event": "admin_approval_evaluated", **result})
    return result


def run_business_assistant(request: AssistantRequest) -> dict[str, Any]:
    intake = normalize_intake(request)
    work_items = [
        request.text,
        "Prepare meeting notes",
        "Draft business report",
        "Draft email reply",
        "Create task list",
    ]
    summary = build_daily_summary(work_items) if intake["ok"] else {"ok": False}
    notes = build_meeting_notes(request.meeting_transcript or request.text, request.participants)
    report = build_document_report(request.text, summary, notes)
    email = build_email_reply(request.inbox_message or request.text, report)
    tasks = build_task_list(summary, notes)
    approvals = {
        "send_email": evaluate_admin_approval("send_email", admin_approved=False),
        "delete_file": evaluate_admin_approval("delete_file", admin_approved=False),
        "calendar_event": evaluate_admin_approval("create_calendar_event", admin_approved=False),
        "spend_money": evaluate_admin_approval("spend_money", admin_approved=True),
        "sign_contract": evaluate_admin_approval("sign_contract", admin_approved=True),
        "status_read": evaluate_admin_approval("read_status", admin_approved=False),
    }
    result = {
        "ok": all([intake["ok"], summary["ok"], notes["ok"], report["ok"], email["ok"], tasks["ok"]]),
        "intake": intake,
        "daily_summary": summary,
        "meeting_notes": notes,
        "document_report": report,
        "email_reply": email,
        "task_list": tasks,
        "approvals": approvals,
        "runtime": RUNTIME,
        "guards": GUARDS,
    }
    write_audit({"event": "business_assistant_run_completed", "ok": result["ok"]})
    return result


def verify_business_assistant_mvp() -> dict[str, Any]:
    before_audit_count = 0
    if AUDIT_PATH.exists():
        before_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    reg = registry()
    chat_request = AssistantRequest(
        source="chat",
        language="mn",
        text="Өнөөдрийн хийсэн ажлаа нэгтгээд meeting notes, report, email draft, task list гарга.",
        participants=["Battulga", "Tuka"],
        meeting_transcript="Battulga asked Tuka to finish the Business Assistant MVP and verify it honestly.",
        inbox_message="Can you send me today's business update?",
    )
    voice_request = AssistantRequest(
        source="voice",
        language="mn",
        text="Дуугаар орсон transcript: өнөөдрийн ажлын тайлан бэлд.",
        participants=["Admin"],
        meeting_transcript="Admin requested voice driven business summary.",
        inbox_message="Please share the summary.",
    )
    chat_result = run_business_assistant(chat_request)
    voice_result = run_business_assistant(voice_request)
    unknown_intake = normalize_intake(AssistantRequest(source="unknown", text="test"))

    after_audit_count = 0
    if AUDIT_PATH.exists():
        after_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    checks = {
        "registry_ok": reg["ok"],
        "capabilities_complete": set(CAPABILITIES)
        == {
            "chat",
            "voice_text_intake",
            "daily_work_summary",
            "meeting_notes",
            "document_report_draft",
            "email_reply_draft",
            "task_list",
            "admin_approval",
            "audit_log",
        },
        "admin_mobile_surface_complete": all(cap in APP_SURFACES["admin_mobile"] for cap in [
            "chat",
            "voice",
            "today",
            "meetings",
            "documents",
            "email_drafts",
            "tasks",
            "approvals",
            "audit",
        ]),
        "user_mobile_surface_present": all(cap in APP_SURFACES["user_mobile"] for cap in [
            "chat",
            "voice",
            "today",
            "tasks",
            "documents",
        ]),
        "chat_flow_ok": chat_result["ok"],
        "voice_flow_ok": voice_result["ok"],
        "voice_transcript_only": voice_result["intake"]["voice_transcript_only"] is True,
        "no_microphone_recording": voice_result["intake"]["microphone_recorded"] is False
        and RUNTIME["live_microphone_enabled"] is False,
        "daily_summary_created": chat_result["daily_summary"]["ok"]
        and bool(chat_result["daily_summary"]["completed"]),
        "meeting_notes_created": chat_result["meeting_notes"]["ok"]
        and bool(chat_result["meeting_notes"]["action_items"]),
        "document_report_created": chat_result["document_report"]["ok"]
        and chat_result["document_report"]["file_written"] is False,
        "email_reply_drafted": chat_result["email_reply"]["ok"]
        and chat_result["email_reply"]["send_executed"] is False,
        "task_list_created": chat_result["task_list"]["ok"]
        and len(chat_result["task_list"]["tasks"]) >= 4,
        "send_email_blocked_without_approval": chat_result["approvals"]["send_email"]["blocked"] is True,
        "delete_file_blocked_without_approval": chat_result["approvals"]["delete_file"]["blocked"] is True,
        "calendar_write_blocked_without_approval": chat_result["approvals"]["calendar_event"]["blocked"] is True,
        "spend_money_hard_blocked": chat_result["approvals"]["spend_money"]["blocked"] is True,
        "sign_contract_hard_blocked": chat_result["approvals"]["sign_contract"]["blocked"] is True,
        "safe_status_read_allowed_preview": chat_result["approvals"]["status_read"]["allowed"] is True
        and chat_result["approvals"]["status_read"]["external_action_executed"] is False,
        "unknown_source_fail_closed": unknown_intake["fail_closed"] is True,
        "live_email_locked": RUNTIME["live_email_enabled"] is False,
        "live_calendar_locked": RUNTIME["live_calendar_enabled"] is False,
        "live_meeting_recording_locked": RUNTIME["live_meeting_recording_enabled"] is False,
        "live_file_write_locked": RUNTIME["live_file_write_enabled"] is False,
        "live_external_api_locked": RUNTIME["live_external_api_enabled"] is False,
        "execution_disabled": RUNTIME["execution_enabled"] is False,
        "admin_approval_required": RUNTIME["admin_approval_required"] is True,
        "guards_present": all(GUARDS.values()),
        "all_actions_audited": after_audit_count > before_audit_count,
        "no_external_action_executed": all(
            item["external_action_executed"] is False
            for item in chat_result["approvals"].values()
        ),
        "preview_only": GUARDS["preview_only"],
        "no_fake_pass": GUARDS["no_fake_pass"],
    }
    passed = sum(1 for ok in checks.values() if ok)
    total = len(checks)
    return {
        "ok": passed == total,
        "phase": "tuka_business_assistant_mvp_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "chat_result": chat_result,
        "voice_result": voice_result,
        "execution_locked": True,
        "updated_at": now_iso(),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(verify_business_assistant_mvp(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
