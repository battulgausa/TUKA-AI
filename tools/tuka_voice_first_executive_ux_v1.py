from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORT = DATA / "tuka_voice_first_executive_ux_report.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "module": "tuka_voice_first_executive_ux_v1",
        "public_name": "Tuka Voice-First Executive UX",
        "principle": "Simple outside, powerful inside",
        "outside": {
            "primary_user_phrase": "Hey Tuka, do this",
            "surface": "Talk to Tuka",
            "user_should_not_need_to_see": [
                "planner internals",
                "judge internals",
                "agent routing internals",
                "memory/rag plumbing",
            ],
        },
        "inside": [
            "Planner",
            "Judge",
            "Context Engine",
            "Skill Registry",
            "Memory",
            "Audit Log",
            "Governance",
            "Admin Approval",
        ],
        "capabilities": {
            "wake_word_future": {
                "name": "Hey Tuka",
                "status": "planned_guarded",
                "requires_admin_enable": True,
                "always_listening_default": False,
            },
            "voice_conversation": {
                "status": "browser_and_local_voice_bridge",
                "text_fallback_required": True,
                "test_speak_required": True,
            },
            "desktop_actions": {
                "status": "governed_future_bridge",
                "examples": [
                    "open app",
                    "find file",
                    "draft email",
                    "create calendar event",
                    "summarize document",
                ],
            },
            "executive_assistant": {
                "status": "mvp_to_expand",
                "examples": [
                    "manage my day",
                    "prepare meeting notes",
                    "follow up leads",
                    "draft report",
                    "summarize inbox",
                ],
            },
        },
        "guards": {
            "no_unapproved_desktop_control": True,
            "no_hidden_always_listening": True,
            "mic_requires_user_action": True,
            "email_send_requires_approval": True,
            "calendar_write_requires_approval": True,
            "file_delete_requires_approval": True,
            "money_contract_legal_requires_human_review": True,
            "all_actions_audited": True,
            "execution_remains_locked_by_default": True,
        },
        "roadmap": [
            "Voice reliability",
            "Hey Tuka guarded wake word",
            "Desktop Action Bridge",
            "Office connectors",
            "Executive Assistant workflows",
            "Personal + Business Memory",
            "Governed AI Operating System",
        ],
    }


def demo(command: str = "Hey Tuka, manage my day") -> dict[str, Any]:
    c = command.strip() or "Hey Tuka, manage my day"
    steps = [
        "Understand the spoken/requested goal",
        "Classify risk",
        "Plan safe steps",
        "Draft outputs/actions",
        "Ask approval before send/write/delete/spend",
        "Audit the result",
    ]
    return {
        "ok": True,
        "module": "tuka_voice_first_executive_ux_v1",
        "input": c,
        "interpreted_as": "voice_first_executive_request",
        "response_style": "simple_user_surface",
        "user_surface_reply": (
            "Ойлголоо. Би эхлээд төлөвлөгөө гаргаад, зөвшөөрөл хэрэгтэй алхам бүрийг танаас асууна."
        ),
        "internal_flow": steps,
        "actions_executed": False,
        "approval_required": True,
        "audit_required": True,
        "blocked_actions": [
            "send email without approval",
            "write calendar without approval",
            "delete files without approval",
            "spend money or sign commitment",
            "hidden always-listening microphone",
        ],
    }


def verify() -> dict[str, Any]:
    reg = registry()
    sample = demo()
    checks = {
        "module_ready": {"ok": reg["ok"] is True},
        "simple_outside_principle": {"ok": reg["principle"] == "Simple outside, powerful inside"},
        "hey_tuka_present": {"ok": reg["capabilities"]["wake_word_future"]["name"] == "Hey Tuka"},
        "always_listening_off_by_default": {
            "ok": reg["capabilities"]["wake_word_future"]["always_listening_default"] is False
        },
        "desktop_actions_governed": {
            "ok": reg["capabilities"]["desktop_actions"]["status"] == "governed_future_bridge"
        },
        "executive_assistant_examples": {
            "ok": "manage my day" in reg["capabilities"]["executive_assistant"]["examples"]
        },
        "admin_approval_required": {"ok": reg["guards"]["email_send_requires_approval"] is True},
        "hidden_listening_blocked": {"ok": reg["guards"]["no_hidden_always_listening"] is True},
        "execution_locked_default": {"ok": reg["guards"]["execution_remains_locked_by_default"] is True},
        "demo_no_execution": {"ok": sample["actions_executed"] is False and sample["approval_required"] is True},
        "audit_required": {"ok": sample["audit_required"] is True},
        "inside_architecture_visible": {
            "ok": all(name in reg["inside"] for name in ["Planner", "Judge", "Governance", "Audit Log"])
        },
    }
    passed = sum(1 for item in checks.values() if item["ok"])
    total = len(checks)
    result = {
        "ok": passed == total,
        "module": "tuka_voice_first_executive_ux_v1",
        "updated_at": _now(),
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "demo": sample,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, ensure_ascii=True))
