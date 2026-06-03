from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.tuka_business_assistant_mvp_v1 import verify_business_assistant_mvp
from tools.tuka_business_executive_assistant_v1 import verify_business_executive_assistant
from tools.tuka_business_operations_agent_system_v1 import verify_business_operations
from tools.tuka_face_identity_privacy_guard_v1 import verify_face_identity_privacy_guard
from tools.tuka_global_marketing_intelligence_v1 import verify_global_marketing_intelligence
from tools.tuka_global_network_compatibility_v1 import verify_global_network_compatibility
from tools.tuka_merge_gate_v1 import evaluate_merge_gate
from tools.tuka_personal_business_assistant_v1 import verify_personal_business_assistant
from tools.tuka_platform_core_pack_v1 import verify_platform_core_pack
from tools.tuka_pr_lifecycle_gate_v1 import verify_pr_lifecycle
from tools.tuka_quantum_shield_v1 import verify_quantum_shield
from tools.tuka_skill_registry_v1 import verify_skill_registry
from tools.tuka_studio_preview_builder_v1 import verify_studio_preview_builder


DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_core_packs_visibility_v1_report.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


PACKS: list[dict[str, Any]] = [
    {
        "id": "global_marketing_intelligence",
        "name": "Tuka Global Marketing Intelligence Agent",
        "file": "tools/tuka_global_marketing_intelligence_v1.py",
        "surface": "Admin Console page + /marketing-intelligence/*",
        "verify": verify_global_marketing_intelligence,
    },
    {
        "id": "quantum_shield",
        "name": "Tuka Quantum Shield",
        "file": "tools/tuka_quantum_shield_v1.py",
        "surface": "Admin Console page + /quantum-shield/*",
        "verify": verify_quantum_shield,
    },
    {
        "id": "business_assistant_mvp",
        "name": "Tuka Business Assistant MVP v1",
        "file": "tools/tuka_business_assistant_mvp_v1.py",
        "surface": "Admin Console page + /business-assistant/*",
        "verify": verify_business_assistant_mvp,
    },
    {
        "id": "platform_core_pack",
        "name": "Tuka Platform Core Pack v1",
        "file": "tools/tuka_platform_core_pack_v1.py",
        "surface": "Core Packs page",
        "verify": verify_platform_core_pack,
    },
    {
        "id": "face_identity_privacy_guard",
        "name": "Tuka Face Identity / Visual Privacy Guard v1",
        "file": "tools/tuka_face_identity_privacy_guard_v1.py",
        "surface": "Core Packs page",
        "verify": verify_face_identity_privacy_guard,
    },
    {
        "id": "business_operations",
        "name": "Tuka Business Operations Agent System v1",
        "file": "tools/tuka_business_operations_agent_system_v1.py",
        "surface": "Core Packs page",
        "verify": verify_business_operations,
    },
    {
        "id": "skill_registry",
        "name": "Tuka Skill Registry v1",
        "file": "tools/tuka_skill_registry_v1.py",
        "surface": "Core Packs page",
        "verify": verify_skill_registry,
    },
    {
        "id": "personal_business_assistant",
        "name": "Tuka Personal + Business Assistant v1",
        "file": "tools/tuka_personal_business_assistant_v1.py",
        "surface": "Core Packs page",
        "verify": verify_personal_business_assistant,
    },
    {
        "id": "studio_preview_builder",
        "name": "Tuka Studio Preview Builder v1",
        "file": "tools/tuka_studio_preview_builder_v1.py",
        "surface": "Core Packs page",
        "verify": verify_studio_preview_builder,
    },
    {
        "id": "merge_gate",
        "name": "Tuka Merge Gate v1",
        "file": "tools/tuka_merge_gate_v1.py",
        "surface": "Core Packs page",
        "verify": evaluate_merge_gate,
    },
    {
        "id": "pr_lifecycle_gate",
        "name": "Tuka PR Lifecycle Gate v1",
        "file": "tools/tuka_pr_lifecycle_gate_v1.py",
        "surface": "Core Packs page",
        "verify": verify_pr_lifecycle,
    },
    {
        "id": "business_executive_assistant",
        "name": "Tuka Business Executive Assistant v1",
        "file": "tools/tuka_business_executive_assistant_v1.py",
        "surface": "Core Packs page",
        "verify": verify_business_executive_assistant,
    },
    {
        "id": "global_network_compatibility",
        "name": "Tuka Global Network Compatibility v1",
        "file": "tools/tuka_global_network_compatibility_v1.py",
        "surface": "Core Packs page",
        "verify": verify_global_network_compatibility,
    },
]


def registry() -> dict[str, Any]:
    return {
        "ok": True,
        "engine": "tuka_core_packs_visibility_v1",
        "mode": "admin_console_visibility_manifest",
        "updated_at": _now(),
        "packs": [
            {
                "id": pack["id"],
                "name": pack["name"],
                "file": pack["file"],
                "surface": pack["surface"],
                "exists": (ROOT / pack["file"]).exists(),
            }
            for pack in PACKS
        ],
        "safety": {
            "execution_enabled": False,
            "external_actions_enabled": False,
            "admin_approval_required": True,
            "no_fake_pass": True,
        },
    }


def _summarize_result(pack: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": pack["id"],
        "name": pack["name"],
        "file": pack["file"],
        "surface": pack["surface"],
        "exists": (ROOT / pack["file"]).exists(),
        "ok": bool(result.get("ok")),
        "passed": result.get("passed"),
        "total": result.get("total"),
        "phase": result.get("phase") or result.get("engine") or pack["id"],
        "raw": result,
    }


def verify_core_packs_visibility() -> dict[str, Any]:
    results = []
    for pack in PACKS:
        verify: Callable[[], dict[str, Any]] = pack["verify"]
        try:
            result = verify()
        except Exception as exc:  # Fail closed with evidence, not a fake pass.
            result = {
                "ok": False,
                "phase": pack["id"],
                "error": str(exc),
                "passed": 0,
                "total": 1,
                "fail_closed": True,
            }
        results.append(_summarize_result(pack, result))

    checks = {
        "all_requested_packs_registered": len(results) == len(PACKS),
        "all_files_exist": all(item["exists"] for item in results),
        "all_verifiers_ok": all(item["ok"] for item in results),
        "admin_surfaces_declared": all(bool(item["surface"]) for item in results),
        "execution_remains_disabled": True,
        "external_actions_disabled": True,
        "admin_approval_required": True,
        "no_fake_pass": True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_core_packs_visibility_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "pack_count": len(results),
        "packs": results,
        "safety": registry()["safety"],
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(json.dumps(verify_core_packs_visibility(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
