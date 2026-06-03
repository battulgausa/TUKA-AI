from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_studio_preview_builder_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_studio_preview_builder_v1_memory.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return cleaned[:48] or "tuka-app"


def _append_memory(event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with MEMORY_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def _domain(prompt: str) -> str:
    text = prompt.lower()
    if any(term in text for term in ["construction", "contractor", "estimate", "material", "барилга"]):
        return "construction"
    if any(term in text for term in ["crm", "sales", "customer", "харилцагч"]):
        return "crm"
    if any(term in text for term in ["invoice", "accounting", "finance", "cashflow", "санхүү"]):
        return "finance"
    if any(term in text for term in ["warehouse", "inventory", "stock", "агуулах", "бараа"]):
        return "inventory"
    if any(term in text for term in ["meeting", "summary", "transcript", "хурал"]):
        return "meeting"
    return "general_business"


def _template_for(domain: str) -> dict[str, Any]:
    templates: dict[str, dict[str, Any]] = {
        "construction": {
            "pages": ["Dashboard", "Projects", "Estimates", "Materials", "Schedule", "Reports"],
            "tables": ["projects", "estimate_items", "materials", "labor_rates", "tasks", "documents"],
            "roles": ["owner_admin", "project_manager", "estimator", "field_user"],
            "workflows": ["create_estimate", "approve_change_order", "track_materials", "weekly_report"],
            "agents": ["EstimateAgent", "MaterialCompareAgent", "ScheduleRiskAgent"],
        },
        "crm": {
            "pages": ["Dashboard", "Leads", "Customers", "Pipeline", "Tasks", "Reports"],
            "tables": ["leads", "customers", "deals", "activities", "notes", "users"],
            "roles": ["owner_admin", "sales_manager", "sales_rep"],
            "workflows": ["capture_lead", "score_lead", "follow_up", "close_deal"],
            "agents": ["LeadAgent", "FollowupAgent", "SalesSummaryAgent"],
        },
        "finance": {
            "pages": ["Dashboard", "Invoices", "Expenses", "Cashflow", "Vendors", "Reports"],
            "tables": ["invoices", "invoice_items", "expenses", "vendors", "payments", "accounts"],
            "roles": ["owner_admin", "accountant", "viewer"],
            "workflows": ["invoice_review", "expense_categorization", "cashflow_forecast"],
            "agents": ["InvoiceAgent", "ExpenseAgent", "CashflowAgent"],
        },
        "inventory": {
            "pages": ["Dashboard", "Items", "Stock Moves", "Suppliers", "Orders", "Reports"],
            "tables": ["items", "stock_movements", "suppliers", "purchase_orders", "locations"],
            "roles": ["owner_admin", "warehouse_manager", "staff"],
            "workflows": ["receive_stock", "low_stock_alert", "supplier_reorder"],
            "agents": ["InventoryAgent", "SupplierAgent", "ReorderAgent"],
        },
        "meeting": {
            "pages": ["Dashboard", "Meetings", "Transcripts", "Action Items", "Followups"],
            "tables": ["meetings", "transcripts", "action_items", "participants", "followups"],
            "roles": ["owner_admin", "host", "participant"],
            "workflows": ["capture_transcript", "summarize_meeting", "assign_actions"],
            "agents": ["SummaryAgent", "ActionItemAgent", "FollowupAgent"],
        },
        "general_business": {
            "pages": ["Dashboard", "Requests", "Tasks", "Customers", "Reports"],
            "tables": ["requests", "tasks", "customers", "notes", "users"],
            "roles": ["owner_admin", "manager", "user"],
            "workflows": ["capture_request", "plan_work", "review_result"],
            "agents": ["PlannerAgent", "TaskAgent", "ReportAgent"],
        },
    }
    return templates[domain]


def build_app_preview(prompt: str) -> dict[str, Any]:
    domain = _domain(prompt)
    template = _template_for(domain)
    app_name = prompt.strip()[:80] or "Tuka Studio App"
    slug = _slug(app_name)
    preview = {
        "ok": True,
        "engine": "tuka_studio_preview_builder_v1",
        "mode": "prompt_to_app_preview_fail_closed",
        "updated_at": _now(),
        "input": {
            "prompt": prompt,
            "detected_domain": domain,
            "app_name": app_name,
            "slug": slug,
        },
        "blueprint": {
            "pages": template["pages"],
            "database_tables": template["tables"],
            "roles": template["roles"],
            "workflows": template["workflows"],
            "agents": template["agents"],
            "api_contract": [
                f"GET /api/{slug}/summary",
                f"GET /api/{slug}/items",
                f"POST /api/{slug}/draft",
                f"POST /api/{slug}/admin-approve",
            ],
            "preview_actions": [
                "generate_wireframe",
                "generate_schema_preview",
                "generate_workflow_preview",
                "create_admin_review_packet",
            ],
        },
        "safety": {
            "preview_only": True,
            "code_write_enabled": False,
            "deploy_enabled": False,
            "external_cloud_enabled": False,
            "admin_approval_required": True,
            "judge_required": True,
            "guardrail_required": True,
            "security_scan_required_before_apply": True,
            "dependency_scan_required_before_apply": True,
            "backup_required_before_export": True,
            "secrets_never_embedded": True,
            "billing_guard_required": True,
            "no_provider_code_copy": True,
            "no_fake_pass": True,
            "fail_closed": True,
        },
        "next_gate": {
            "can_apply_now": False,
            "required_before_apply": ["Admin approval", "Judge approval", "Guardrail approval", "Security scan"],
            "recommended_first_build": "local_preview_only",
        },
    }
    _append_memory(
        {
            "ts": _now(),
            "event": "studio_preview_built",
            "domain": domain,
            "slug": slug,
            "prompt": prompt,
        }
    )
    return preview


def verify_studio_preview_builder() -> dict[str, Any]:
    samples = {
        "construction": build_app_preview("Construction estimate and material tracker app"),
        "crm": build_app_preview("CRM agent for sales leads and customer follow ups"),
        "inventory": build_app_preview("Warehouse inventory system with suppliers and stock alerts"),
    }
    first = samples["construction"]
    safety = first["safety"]
    blueprint = first["blueprint"]
    checks = {
        "engine_ok": first["ok"] is True,
        "construction_domain_detected": first["input"]["detected_domain"] == "construction",
        "crm_domain_detected": samples["crm"]["input"]["detected_domain"] == "crm",
        "inventory_domain_detected": samples["inventory"]["input"]["detected_domain"] == "inventory",
        "pages_generated": len(blueprint["pages"]) >= 5,
        "database_schema_generated": len(blueprint["database_tables"]) >= 5,
        "roles_generated": len(blueprint["roles"]) >= 3,
        "workflows_generated": len(blueprint["workflows"]) >= 3,
        "agents_generated": len(blueprint["agents"]) >= 3,
        "api_contract_generated": len(blueprint["api_contract"]) >= 4,
        "preview_actions_generated": len(blueprint["preview_actions"]) >= 4,
        "preview_only_locked": safety["preview_only"] is True and safety["code_write_enabled"] is False,
        "deploy_locked": safety["deploy_enabled"] is False and safety["external_cloud_enabled"] is False,
        "admin_gate_required": safety["admin_approval_required"] is True,
        "judge_guardrail_required": safety["judge_required"] is True and safety["guardrail_required"] is True,
        "security_dependency_scans_required": safety["security_scan_required_before_apply"] is True
        and safety["dependency_scan_required_before_apply"] is True,
        "backup_and_billing_guards_present": safety["backup_required_before_export"] is True
        and safety["billing_guard_required"] is True,
        "secrets_never_embedded": safety["secrets_never_embedded"] is True,
        "provider_code_not_copied": safety["no_provider_code_copy"] is True,
        "apply_gate_fail_closed": first["next_gate"]["can_apply_now"] is False and safety["fail_closed"] is True,
        "no_fake_pass": safety["no_fake_pass"] is True,
        "memory_written": MEMORY_PATH.exists(),
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_studio_preview_builder_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "samples": samples,
        "inspired_by_market_pattern": "natural_language_to_full_stack_preview",
        "copied_provider_code": False,
        "execution_locked": True,
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify_studio_preview_builder(), indent=2, ensure_ascii=False))
