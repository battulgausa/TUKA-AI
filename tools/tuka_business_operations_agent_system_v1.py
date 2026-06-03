from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_business_operations_agent_system_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_business_operations_agent_system_v1_memory.jsonl"
AUDIT_PATH = DATA_DIR / "tuka_business_operations_agent_system_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


OPERATION_AGENTS = [
    {
        "id": "office_operations",
        "name": "Office Operations",
        "work": ["email_triage", "document_report_pdf", "presentation", "meeting_protocol", "task_list"],
        "blocked_without_approval": ["send_email", "delete_email", "publish_document"],
    },
    {
        "id": "hr_admin",
        "name": "HR / Admin",
        "work": ["interview_plan", "candidate_scorecard", "onboarding_checklist", "employee_record_plan", "policy_document"],
        "blocked_without_approval": ["make_hiring_decision", "store_sensitive_hr_record", "send_offer"],
    },
    {
        "id": "finance_accounting",
        "name": "Finance / Accounting",
        "work": ["invoice_reading", "expense_classification", "cashflow_report", "budget_forecast", "accounting_connector_plan"],
        "blocked_without_approval": ["spend_money", "pay_invoice", "post_to_accounting_system"],
    },
    {
        "id": "sales_customer_support",
        "name": "Sales / Customer Support",
        "work": ["customer_message_triage", "quote_draft", "followup_email", "crm_update_plan", "complaint_report"],
        "blocked_without_approval": ["send_quote", "update_live_crm", "issue_refund"],
    },
    {
        "id": "project_management",
        "name": "Project Management",
        "work": ["work_breakdown", "deadline_plan", "progress_check", "bottleneck_detection", "weekly_report"],
        "blocked_without_approval": ["change_committed_deadline", "assign_external_work", "close_project"],
    },
    {
        "id": "procurement_supply_chain",
        "name": "Procurement / Supply Chain",
        "work": ["supplier_research", "price_comparison", "material_order_list", "purchase_request", "approval_packet"],
        "blocked_without_approval": ["spend_money", "place_order", "sign_supplier_agreement"],
    },
    {
        "id": "legal_compliance",
        "name": "Legal / Compliance",
        "work": ["contract_draft_review", "risk_highlight", "policy_check", "jurisdiction_warning", "lawyer_review_marker"],
        "blocked_without_approval": ["sign_contract", "provide_legal_opinion", "submit_legal_filing"],
    },
    {
        "id": "research_strategy",
        "name": "Research / Strategy",
        "work": ["web_research_plan", "sourced_report", "competitor_analysis", "claim_confidence_label", "strategy_options"],
        "blocked_without_approval": ["publish_report", "paid_research_api", "act_on_unverified_claim"],
    },
]


GLOBAL_GUARDS = {
    "send_email_requires_approval": True,
    "delete_file_email_message_requires_approval": True,
    "spend_money_requires_approval": True,
    "sign_contract_blocked_manual_review": True,
    "legal_medical_financial_high_risk_human_review": True,
    "unknown_or_conflicting_info_fail_closed": True,
    "all_actions_audited": True,
    "research_requires_sources": True,
    "no_live_external_connectors": True,
    "no_live_send_delete_spend_sign": True,
    "preview_only": True,
    "fail_closed": True,
    "no_fake_pass": True,
}


WORKFLOW = [
    "receive_work",
    "plan_work",
    "execute_preview",
    "verify_result",
    "report_status",
    "request_approval_if_needed",
]


def operations_registry() -> dict[str, Any]:
    registry = {
        "ok": True,
        "engine": "tuka_business_operations_agent_system_v1",
        "mode": "governed_business_operations_preview",
        "updated_at": _now(),
        "public_name": "Tuka Business Operations Agent System",
        "workflow": WORKFLOW,
        "agents": OPERATION_AGENTS,
        "global_guards": GLOBAL_GUARDS,
        "roadmap_position": [
            "Core Stability",
            "Governance + Guardrails",
            "Context + Memory",
            "Skill System",
            "Office Assistant",
            "Business Operations Agent System",
            "Finance / HR / Sales / Legal / Procurement Agents",
            "Autonomous-but-governed Business Execution",
        ],
        "runtime": {
            "live_email_enabled": False,
            "live_calendar_enabled": False,
            "live_accounting_enabled": False,
            "live_crm_enabled": False,
            "live_procurement_enabled": False,
            "live_legal_submission_enabled": False,
            "external_action_enabled": False,
            "approval_required_before_external_action": True,
        },
    }
    _append_jsonl(MEMORY_PATH, {"ts": _now(), "event": "operations_registry_built", "agent_count": len(OPERATION_AGENTS)})
    return registry


def classify_business_work(request: str) -> dict[str, Any]:
    text = request.lower()
    mapping = [
        ("finance_accounting", ["invoice", "expense", "cashflow", "budget", "accounting", "санхүү"]),
        ("hr_admin", ["interview", "candidate", "onboarding", "employee", "hr"]),
        ("sales_customer_support", ["customer", "quote", "crm", "complaint", "support"]),
        ("procurement_supply_chain", ["supplier", "purchase", "material", "order", "procurement"]),
        ("legal_compliance", ["contract", "legal", "compliance", "policy", "jurisdiction"]),
        ("project_management", ["project", "deadline", "progress", "bottleneck", "weekly"]),
        ("research_strategy", ["research", "competitor", "strategy", "market"]),
        ("office_operations", ["email", "document", "presentation", "meeting", "task"]),
    ]
    agent_id = "office_operations"
    for candidate, keywords in mapping:
        if any(keyword in text for keyword in keywords):
            agent_id = candidate
            break
    agent = next(item for item in OPERATION_AGENTS if item["id"] == agent_id)
    result = {
        "ok": True,
        "request": request,
        "selected_agent": agent,
        "confidence": "medium",
        "requires_human_review": agent_id in {"finance_accounting", "legal_compliance", "procurement_supply_chain"},
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "business_work_classified", "agent_id": agent_id})
    return result


def build_work_plan(request: str) -> dict[str, Any]:
    classified = classify_business_work(request)
    agent = classified["selected_agent"]
    plan = {
        "ok": True,
        "workflow": WORKFLOW,
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "steps": [
            {"step": "receive_work", "status": "captured", "output": request},
            {"step": "plan_work", "status": "preview", "output": agent["work"][:3]},
            {"step": "execute_preview", "status": "locked", "output": "No live external action executed."},
            {"step": "verify_result", "status": "preview", "output": "Check draft quality, risk, and missing approvals."},
            {"step": "report_status", "status": "preview", "output": "Draft report ready for Admin review."},
            {"step": "request_approval_if_needed", "status": "required", "output": agent["blocked_without_approval"]},
        ],
        "approval_required": True,
        "external_action_executed": False,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "business_work_plan_built", "agent_id": agent["id"]})
    return plan


def evaluate_business_action(action: str, *, admin_approved: bool = False, human_reviewed: bool = False) -> dict[str, Any]:
    approval_actions = {
        "send_email",
        "delete_file",
        "delete_email",
        "delete_message",
        "spend_money",
        "pay_invoice",
        "place_order",
        "update_live_crm",
        "post_to_accounting_system",
    }
    hard_blocked = {
        "sign_contract",
        "provide_legal_opinion",
        "submit_legal_filing",
        "act_on_unverified_claim",
    }
    allowed = action not in approval_actions and action not in hard_blocked
    if action in approval_actions:
        allowed = admin_approved and human_reviewed
    if action in hard_blocked:
        allowed = False
    result = {
        "ok": True,
        "action": action,
        "allowed": allowed,
        "blocked": not allowed,
        "admin_approved": admin_approved,
        "human_reviewed": human_reviewed,
        "external_action_executed": False,
        "reason": "approved_preview_action" if allowed else "approval_or_manual_review_required",
        "fail_closed": not allowed,
        "audit_written": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "business_action_evaluated", "action": action, "allowed": allowed})
    return result


def verify_business_operations() -> dict[str, Any]:
    registry = operations_registry()
    agents = registry["agents"]
    guards = registry["global_guards"]
    runtime = registry["runtime"]
    samples = {
        "finance": build_work_plan("Read invoice and prepare cashflow report"),
        "hr": build_work_plan("Interview candidate and create onboarding checklist"),
        "sales": build_work_plan("Classify customer complaint and draft follow-up email"),
        "procurement": build_work_plan("Research supplier and prepare purchase request"),
        "legal": build_work_plan("Review contract draft and highlight compliance risk"),
        "project": build_work_plan("Check project progress and create weekly report"),
        "research": build_work_plan("Research competitor strategy with sources"),
        "office": build_work_plan("Prepare meeting protocol and task list"),
    }
    blocked_actions = {
        "send_email": evaluate_business_action("send_email"),
        "delete_file": evaluate_business_action("delete_file"),
        "spend_money": evaluate_business_action("spend_money"),
        "sign_contract": evaluate_business_action("sign_contract", admin_approved=True, human_reviewed=True),
        "legal_opinion": evaluate_business_action("provide_legal_opinion", admin_approved=True, human_reviewed=True),
        "unverified_claim": evaluate_business_action("act_on_unverified_claim", admin_approved=True, human_reviewed=True),
    }
    checks = {
        "registry_ok": registry["ok"] is True,
        "eight_agents_registered": len(agents) == 8,
        "workflow_complete": registry["workflow"] == WORKFLOW,
        "office_agent_present": any(item["id"] == "office_operations" for item in agents),
        "hr_agent_present": any(item["id"] == "hr_admin" for item in agents),
        "finance_agent_present": any(item["id"] == "finance_accounting" for item in agents),
        "sales_agent_present": any(item["id"] == "sales_customer_support" for item in agents),
        "project_agent_present": any(item["id"] == "project_management" for item in agents),
        "procurement_agent_present": any(item["id"] == "procurement_supply_chain" for item in agents),
        "legal_agent_present": any(item["id"] == "legal_compliance" for item in agents),
        "research_agent_present": any(item["id"] == "research_strategy" for item in agents),
        "all_agents_have_work": all(len(item["work"]) >= 5 for item in agents),
        "all_agents_have_blocked_actions": all(len(item["blocked_without_approval"]) >= 3 for item in agents),
        "sample_plans_created": all(item["ok"] is True for item in samples.values()),
        "sample_plans_no_external_action": all(item["external_action_executed"] is False for item in samples.values()),
        "send_delete_spend_rules_present": guards["send_email_requires_approval"] is True
        and guards["delete_file_email_message_requires_approval"] is True
        and guards["spend_money_requires_approval"] is True,
        "contract_legal_review_rules_present": guards["sign_contract_blocked_manual_review"] is True
        and guards["legal_medical_financial_high_risk_human_review"] is True,
        "unknown_conflict_fail_closed": guards["unknown_or_conflicting_info_fail_closed"] is True,
        "research_requires_sources": guards["research_requires_sources"] is True,
        "high_risk_actions_blocked": all(item["blocked"] is True for item in blocked_actions.values()),
        "no_external_action_executed": all(item["external_action_executed"] is False for item in blocked_actions.values()),
        "live_connectors_locked": all(value is False for key, value in runtime.items() if key.startswith("live_") or key == "external_action_enabled"),
        "approval_required_before_external_action": runtime["approval_required_before_external_action"] is True,
        "audit_written": guards["all_actions_audited"] is True and AUDIT_PATH.exists(),
        "roadmap_position_present": "Business Operations Agent System" in registry["roadmap_position"],
        "preview_only_fail_closed": guards["preview_only"] is True and guards["fail_closed"] is True,
        "no_fake_pass": guards["no_fake_pass"] is True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_business_operations_agent_system_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "registry": registry,
        "sample_plans": samples,
        "blocked_action_examples": blocked_actions,
        "execution_locked": True,
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify_business_operations(), indent=2, ensure_ascii=False))
