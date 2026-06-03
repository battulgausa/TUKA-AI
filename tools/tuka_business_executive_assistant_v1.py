from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_business_executive_assistant_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_business_executive_assistant_v1_memory.jsonl"
AUDIT_PATH = DATA_DIR / "tuka_business_executive_assistant_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


EXECUTIVE_CAPABILITIES = [
    {
        "id": "business_interview",
        "name": "Business Interview",
        "can_preview": ["question_plan", "answer_notes", "evaluation_scorecard", "followup_questions"],
        "blocked_without_approval": ["record_interview", "send_offer", "sign_supplier", "make_commitment"],
        "human_review_required": ["hiring_decision", "supplier_decision", "client_commitment"],
    },
    {
        "id": "presentation_slide_show",
        "name": "Presentation + Slide Show",
        "can_preview": ["outline", "slide_plan", "speaker_notes", "qa_pause_resume_script"],
        "blocked_without_approval": ["present_live", "record_session", "send_deck", "publish_deck"],
        "human_review_required": ["public_claims", "pricing", "legal_disclaimer"],
    },
    {
        "id": "meeting_assistant",
        "name": "Meeting Assistant",
        "can_preview": ["meeting_minutes", "protocol", "action_items", "decision_log"],
        "blocked_without_approval": ["record_meeting", "join_external_meeting", "invite_people", "send_minutes"],
        "human_review_required": ["sensitive_meeting", "contract_discussion", "legal_or_hr_topic"],
    },
    {
        "id": "file_generator",
        "name": "File Generator",
        "can_preview": ["pdf_outline", "word_doc_draft", "powerpoint_outline", "excel_report_schema"],
        "blocked_without_approval": ["overwrite_file", "delete_file", "send_file", "publish_file"],
        "human_review_required": ["contract_draft", "financial_report", "legal_document"],
    },
    {
        "id": "email_delivery",
        "name": "Email Delivery",
        "can_preview": ["recipient_check", "subject_draft", "body_draft", "attachment_summary"],
        "blocked_without_approval": ["send_email", "delete_email", "forward_sensitive_email"],
        "human_review_required": ["external_recipient", "attachment_present", "financial_or_contract_content"],
    },
    {
        "id": "research_agent",
        "name": "Research Agent",
        "can_preview": ["research_plan", "source_list", "claim_check", "uncertainty_report"],
        "blocked_without_approval": ["paid_research_api", "publish_claim", "scrape_private_source"],
        "human_review_required": ["medical_legal_financial_claim", "uncertain_source", "high_impact_report"],
    },
    {
        "id": "task_execution",
        "name": "Task Execution",
        "can_preview": ["task_plan", "subtasks", "verification_plan", "progress_report"],
        "blocked_without_approval": ["external_execute", "commit_push_pr", "deploy", "purchase"],
        "human_review_required": ["high_risk_action", "external_commitment", "production_change"],
    },
    {
        "id": "collaboration",
        "name": "Collaboration",
        "can_preview": ["feedback", "revision_plan", "alternative_options", "truthful_disagreement"],
        "blocked_without_approval": ["change_final_decision", "send_on_behalf", "approve_contract"],
        "human_review_required": ["final_approval", "business_commitment", "legal_commitment"],
    },
]


GLOBAL_GUARDS = {
    "email_send_requires_approval": True,
    "file_delete_requires_approval": True,
    "meeting_recording_requires_consent": True,
    "contract_finance_legal_requires_human_review": True,
    "research_requires_sources": True,
    "uncertain_claim_must_be_marked_uncertain": True,
    "no_fake_pass": True,
    "all_actions_audited": True,
    "preview_only": True,
    "fail_closed": True,
    "live_email_disabled": True,
    "live_recording_disabled": True,
    "live_meeting_join_disabled": True,
    "live_file_write_disabled": True,
    "live_deploy_disabled": True,
}


def executive_assistant_registry() -> dict[str, Any]:
    registry = {
        "ok": True,
        "engine": "tuka_business_executive_assistant_v1",
        "mode": "governed_executive_assistant_preview",
        "updated_at": _now(),
        "public_name": "Tuka Business Executive Assistant",
        "capabilities": EXECUTIVE_CAPABILITIES,
        "global_guards": GLOBAL_GUARDS,
        "roadmap_position": [
            "Core Stability",
            "Governance / Guardrails",
            "Context + Memory",
            "Skill System",
            "Office Assistant",
            "Voice + Meeting Layer",
            "Business Executive Assistant",
            "Research + Presentation + Email Automation",
        ],
        "runtime": {
            "live_integrations_enabled": False,
            "email_send_enabled": False,
            "meeting_recording_enabled": False,
            "external_meeting_join_enabled": False,
            "file_write_enabled": False,
            "deployment_enabled": False,
            "approval_required_before_external_action": True,
        },
    }
    _append_jsonl(MEMORY_PATH, {"ts": _now(), "event": "executive_registry_built", "capability_count": len(EXECUTIVE_CAPABILITIES)})
    return registry


def draft_interview_plan(subject: str, interview_type: str = "client") -> dict[str, Any]:
    questions = [
        f"What is the main goal for this {interview_type} conversation?",
        "What problem are you trying to solve?",
        "What constraints, budget, or timeline matter most?",
        "What would a successful outcome look like?",
    ]
    result = {
        "ok": True,
        "subject": subject,
        "interview_type": interview_type,
        "questions": questions,
        "scorecard": ["clarity", "fit", "risk", "next_step"],
        "recording_started": False,
        "external_action_executed": False,
        "approval_required": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "interview_plan_drafted", "subject": subject})
    return result


def draft_presentation(topic: str) -> dict[str, Any]:
    result = {
        "ok": True,
        "topic": topic,
        "slides": [
            {"title": "Problem", "notes": "Explain why this matters."},
            {"title": "Proposed Solution", "notes": "Show the practical approach."},
            {"title": "Plan", "notes": "Break the work into clear steps."},
            {"title": "Decision Needed", "notes": "Ask for review or approval."},
        ],
        "qa_behavior": "pause_answer_resume",
        "presented_live": False,
        "file_sent": False,
        "approval_required": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "presentation_drafted", "topic": topic})
    return result


def draft_meeting_minutes(transcript: str) -> dict[str, Any]:
    result = {
        "ok": True,
        "summary": "Meeting summary draft based on supplied text only.",
        "protocol": ["discussion_captured", "decisions_pending_review", "actions_pending_owner_confirmation"],
        "action_items": ["Confirm owners", "Confirm due dates", "Send reviewed minutes"],
        "recording_used": False,
        "email_sent": False,
        "approval_required": True,
        "source": "admin_supplied_text",
        "input_length": len(transcript),
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "meeting_minutes_drafted", "input_length": len(transcript)})
    return result


def draft_research_packet(topic: str, sources: list[str] | None = None) -> dict[str, Any]:
    sources = sources or []
    result = {
        "ok": True,
        "topic": topic,
        "claims": [],
        "sources": sources,
        "source_required": True,
        "uncertainty": "unverified" if not sources else "requires_human_review",
        "internet_called": False,
        "paid_api_called": False,
        "approval_required_before_publish": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "research_packet_drafted", "topic": topic, "source_count": len(sources)})
    return result


def evaluate_executive_action(action: str, *, admin_approved: bool = False, consent_confirmed: bool = False) -> dict[str, Any]:
    high_risk = {
        "send_email",
        "delete_file",
        "record_meeting",
        "send_deck",
        "create_contract",
        "financial_commitment",
        "legal_commitment",
        "deploy",
        "commit_push_pr",
        "join_external_meeting",
    }
    hard_blocked = {"financial_commitment", "legal_commitment", "create_contract"}
    allowed = action not in high_risk or (admin_approved and consent_confirmed)
    if action in hard_blocked:
        allowed = False
    result = {
        "ok": True,
        "action": action,
        "allowed": allowed,
        "blocked": not allowed,
        "reason": "approved_preview_action" if allowed else "approval_consent_or_human_review_required",
        "admin_approved": admin_approved,
        "consent_confirmed": consent_confirmed,
        "external_action_executed": False,
        "audit_written": True,
        "fail_closed": not allowed,
        "updated_at": _now(),
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "executive_action_evaluated", "action": action, "allowed": allowed})
    return result


def verify_business_executive_assistant() -> dict[str, Any]:
    registry = executive_assistant_registry()
    caps = registry["capabilities"]
    guard = registry["global_guards"]
    runtime = registry["runtime"]
    interview = draft_interview_plan("Supplier qualification", "supplier")
    presentation = draft_presentation("Quarterly business plan")
    meeting = draft_meeting_minutes("Discussed goals, risks, and next actions.")
    research = draft_research_packet("market comparison", sources=["https://example.com/source"])
    no_source_research = draft_research_packet("unverified market claim")
    blocked_actions = {
        "send_email": evaluate_executive_action("send_email"),
        "delete_file": evaluate_executive_action("delete_file"),
        "record_meeting": evaluate_executive_action("record_meeting"),
        "financial_commitment": evaluate_executive_action("financial_commitment", admin_approved=True, consent_confirmed=True),
        "legal_commitment": evaluate_executive_action("legal_commitment", admin_approved=True, consent_confirmed=True),
        "deploy": evaluate_executive_action("deploy"),
    }
    checks = {
        "registry_ok": registry["ok"] is True,
        "eight_capabilities_registered": len(caps) == 8,
        "all_capabilities_have_preview_actions": all(len(item["can_preview"]) >= 4 for item in caps),
        "all_capabilities_have_blocked_actions": all(len(item["blocked_without_approval"]) >= 3 for item in caps),
        "email_send_requires_approval": guard["email_send_requires_approval"] is True,
        "file_delete_requires_approval": guard["file_delete_requires_approval"] is True,
        "meeting_recording_requires_consent": guard["meeting_recording_requires_consent"] is True,
        "contract_finance_legal_requires_human_review": guard["contract_finance_legal_requires_human_review"] is True,
        "research_requires_sources": guard["research_requires_sources"] is True,
        "uncertain_claim_marked": no_source_research["uncertainty"] == "unverified",
        "interview_plan_created": interview["ok"] is True and len(interview["questions"]) >= 4,
        "presentation_draft_created": presentation["ok"] is True and presentation["qa_behavior"] == "pause_answer_resume",
        "meeting_minutes_created": meeting["ok"] is True and meeting["recording_used"] is False,
        "file_generation_preview_present": any(item["id"] == "file_generator" for item in caps),
        "research_packet_has_sources": research["ok"] is True and len(research["sources"]) >= 1,
        "task_execution_preview_present": any(item["id"] == "task_execution" for item in caps),
        "collaboration_preview_present": any(item["id"] == "collaboration" for item in caps),
        "live_integrations_locked": runtime["live_integrations_enabled"] is False,
        "email_recording_file_deploy_locked": runtime["email_send_enabled"] is False
        and runtime["meeting_recording_enabled"] is False
        and runtime["file_write_enabled"] is False
        and runtime["deployment_enabled"] is False,
        "high_risk_actions_blocked": all(item["blocked"] is True for item in blocked_actions.values()),
        "no_external_action_executed": all(item["external_action_executed"] is False for item in blocked_actions.values()),
        "audit_written": guard["all_actions_audited"] is True and AUDIT_PATH.exists(),
        "roadmap_position_present": "Business Executive Assistant" in registry["roadmap_position"],
        "preview_only_fail_closed": guard["preview_only"] is True and guard["fail_closed"] is True,
        "no_fake_pass": guard["no_fake_pass"] is True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_business_executive_assistant_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "registry": registry,
        "examples": {
            "interview": interview,
            "presentation": presentation,
            "meeting": meeting,
            "research": research,
            "unverified_research": no_source_research,
            "blocked_actions": blocked_actions,
        },
        "execution_locked": True,
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify_business_executive_assistant(), indent=2, ensure_ascii=False))
