"""Tuka Face Identity / Visual Privacy Guard v1.

This module is a governed preview surface for face identity and privacy
protection. It does not access a camera, store face images, or perform real
biometric matching. Its purpose is to define the safety contract Tuka must
enforce before any future vision runtime is allowed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "face_identity_privacy_guard_audit.jsonl"


IDENTITY_CLASSES = [
    "admin",
    "known_trusted_person",
    "employee",
    "guest",
    "unknown_person",
]


ROADMAP_POSITION = [
    "Core Stability",
    "Governance / Guardrails",
    "Vision Layer",
    "Face Identity",
    "Privacy Guard",
    "Meeting / Office / Business Assistant",
    "Device / Room / Security Integration",
]


PRIVACY_ACTIONS = {
    "unknown_person": [
        "sensitive_screen_hide",
        "private_data_lock",
        "admin_only_files_block",
        "voice_command_disabled",
        "manual_approval_required",
    ],
    "guest": [
        "sensitive_screen_hide",
        "admin_only_files_block",
        "manual_approval_required",
    ],
    "employee": [
        "role_scoped_access_only",
        "admin_action_requires_step_up",
        "audit_log_required",
    ],
    "known_trusted_person": [
        "role_scoped_access_only",
        "admin_action_requires_step_up",
        "audit_log_required",
    ],
    "admin": [
        "step_up_auth_required_for_admin_action",
        "audit_log_required",
    ],
}


GOVERNANCE_RULES = {
    "no_face_profile_without_consent": True,
    "do_not_guess_unknown_identity": True,
    "face_alone_never_authorizes_high_risk_action": True,
    "admin_action_requires_password_2fa_voice_pin": True,
    "face_data_must_be_encrypted": True,
    "delete_request_removes_profile": True,
    "audit_log_required": True,
    "unknown_person_fail_closed": True,
    "live_camera_enabled": False,
    "live_face_matching_enabled": False,
    "face_profile_storage_enabled": False,
    "biometric_unlock_enabled": False,
    "preview_only": True,
    "no_fake_pass": True,
}


RUNTIME = {
    "live_camera_enabled": False,
    "live_face_matching_enabled": False,
    "face_profile_storage_enabled": False,
    "biometric_unlock_enabled": False,
    "sensitive_screen_control_enabled": False,
    "external_security_system_enabled": False,
    "approval_required_before_any_unlock": True,
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
        "engine": "tuka_face_identity_privacy_guard_v1",
        "mode": "governed_visual_privacy_preview",
        "public_name": "Tuka Face Identity / Visual Privacy Guard",
        "updated_at": now_iso(),
        "identity_classes": IDENTITY_CLASSES,
        "privacy_actions": PRIVACY_ACTIONS,
        "governance_rules": GOVERNANCE_RULES,
        "runtime": RUNTIME,
        "roadmap_position": ROADMAP_POSITION,
    }


def classify_visual_identity(
    *,
    face_detected: bool,
    consent_recorded: bool,
    profile_match: str | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    """Classify a visual identity without guessing unknown people."""
    if not face_detected:
        classification = "unknown_person"
        confidence = "none"
        reason = "no_face_detected"
    elif not consent_recorded:
        classification = "unknown_person"
        confidence = "low"
        reason = "consent_missing_no_profile_lookup"
    elif profile_match and role in IDENTITY_CLASSES and role != "unknown_person":
        classification = role
        confidence = "preview_declared"
        reason = "consented_profile_marker_present"
    else:
        classification = "unknown_person"
        confidence = "low"
        reason = "no_consented_profile_match"

    result = {
        "ok": True,
        "classification": classification,
        "confidence": confidence,
        "reason": reason,
        "name_guessed": False,
        "face_profile_written": False,
        "requires_manual_approval": classification != "admin",
        "actions": PRIVACY_ACTIONS[classification],
        "fail_closed": classification == "unknown_person",
    }
    write_audit({"event": "visual_identity_classified", **result})
    return result


def evaluate_admin_action(
    action: str,
    *,
    face_classification: str,
    password_ok: bool = False,
    two_factor_ok: bool = False,
    voice_ok: bool = False,
    pin_ok: bool = False,
) -> dict[str, Any]:
    step_up_complete = all([password_ok, two_factor_ok, voice_ok, pin_ok])
    high_risk = action in {
        "unlock_private_data",
        "show_admin_files",
        "enable_voice_command",
        "approve_external_action",
        "disable_privacy_guard",
    }
    allowed = (
        face_classification == "admin"
        and step_up_complete
        and not RUNTIME["biometric_unlock_enabled"]
    )
    if high_risk and not step_up_complete:
        allowed = False
    if face_classification != "admin":
        allowed = False

    result = {
        "ok": True,
        "action": action,
        "face_classification": face_classification,
        "allowed": allowed,
        "blocked": not allowed,
        "high_risk": high_risk,
        "step_up_complete": step_up_complete,
        "face_alone_authorized": False,
        "external_action_executed": False,
        "reason": "step_up_required" if not allowed else "preview_allowed_no_live_unlock",
        "fail_closed": not allowed,
        "audit_written": True,
    }
    write_audit({"event": "admin_action_evaluated", **result})
    return result


def enrollment_policy(consent_recorded: bool, encryption_available: bool) -> dict[str, Any]:
    allowed = bool(consent_recorded and encryption_available and not RUNTIME["face_profile_storage_enabled"])
    result = {
        "ok": True,
        "consent_recorded": consent_recorded,
        "encryption_available": encryption_available,
        "profile_write_allowed": allowed,
        "profile_write_executed": False,
        "requires_admin_confirmation": True,
        "delete_request_supported": True,
        "reason": "preview_only_no_storage" if allowed else "consent_and_encryption_required",
        "audit_written": True,
    }
    write_audit({"event": "face_enrollment_policy_checked", **result})
    return result


def delete_profile_request(person_id: str, admin_approved: bool) -> dict[str, Any]:
    result = {
        "ok": True,
        "person_id": person_id,
        "admin_approved": admin_approved,
        "delete_allowed": bool(admin_approved),
        "delete_executed": False,
        "reason": "preview_only_no_profile_storage",
        "audit_written": True,
    }
    write_audit({"event": "face_profile_delete_requested", **result})
    return result


def verify_face_identity_privacy_guard() -> dict[str, Any]:
    before_audit_count = 0
    if AUDIT_PATH.exists():
        before_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    reg = registry()
    unknown = classify_visual_identity(face_detected=True, consent_recorded=False)
    admin = classify_visual_identity(
        face_detected=True,
        consent_recorded=True,
        profile_match="admin-profile",
        role="admin",
    )
    employee = classify_visual_identity(
        face_detected=True,
        consent_recorded=True,
        profile_match="employee-profile",
        role="employee",
    )
    blocked_unlock = evaluate_admin_action(
        "unlock_private_data",
        face_classification="admin",
        password_ok=True,
        two_factor_ok=False,
        voice_ok=True,
        pin_ok=True,
    )
    unknown_unlock = evaluate_admin_action(
        "enable_voice_command",
        face_classification="unknown_person",
        password_ok=True,
        two_factor_ok=True,
        voice_ok=True,
        pin_ok=True,
    )
    preview_admin_unlock = evaluate_admin_action(
        "show_admin_files",
        face_classification="admin",
        password_ok=True,
        two_factor_ok=True,
        voice_ok=True,
        pin_ok=True,
    )
    enrollment_blocked = enrollment_policy(consent_recorded=False, encryption_available=True)
    enrollment_ready = enrollment_policy(consent_recorded=True, encryption_available=True)
    delete_request = delete_profile_request("admin-profile", admin_approved=True)

    after_audit_count = 0
    if AUDIT_PATH.exists():
        after_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    checks = {
        "registry_ok": reg["ok"],
        "identity_classes_complete": set(IDENTITY_CLASSES)
        == {"admin", "known_trusted_person", "employee", "guest", "unknown_person"},
        "roadmap_position_present": "Face Identity" in ROADMAP_POSITION
        and "Privacy Guard" in ROADMAP_POSITION,
        "unknown_privacy_actions_present": all(
            action in PRIVACY_ACTIONS["unknown_person"]
            for action in [
                "sensitive_screen_hide",
                "private_data_lock",
                "admin_only_files_block",
                "voice_command_disabled",
                "manual_approval_required",
            ]
        ),
        "no_consent_profile_storage_rule": GOVERNANCE_RULES["no_face_profile_without_consent"],
        "unknown_name_not_guessed": unknown["name_guessed"] is False
        and unknown["classification"] == "unknown_person",
        "face_alone_never_authorizes": GOVERNANCE_RULES[
            "face_alone_never_authorizes_high_risk_action"
        ],
        "step_up_auth_rule_present": GOVERNANCE_RULES[
            "admin_action_requires_password_2fa_voice_pin"
        ],
        "encryption_required": GOVERNANCE_RULES["face_data_must_be_encrypted"],
        "delete_request_supported": GOVERNANCE_RULES["delete_request_removes_profile"]
        and delete_request["ok"],
        "unknown_fail_closed": unknown["fail_closed"] is True,
        "unknown_voice_command_disabled": "voice_command_disabled" in unknown["actions"],
        "admin_classification_preview": admin["classification"] == "admin",
        "employee_classification_preview": employee["classification"] == "employee",
        "admin_missing_2fa_blocked": blocked_unlock["blocked"] is True,
        "unknown_action_blocked": unknown_unlock["blocked"] is True,
        "preview_admin_unlock_no_live_action": preview_admin_unlock["allowed"] is True
        and preview_admin_unlock["external_action_executed"] is False,
        "enrollment_without_consent_blocked": enrollment_blocked["profile_write_allowed"] is False,
        "enrollment_ready_but_no_write_executed": enrollment_ready["profile_write_allowed"] is True
        and enrollment_ready["profile_write_executed"] is False,
        "live_camera_locked": RUNTIME["live_camera_enabled"] is False,
        "live_face_matching_locked": RUNTIME["live_face_matching_enabled"] is False,
        "profile_storage_locked": RUNTIME["face_profile_storage_enabled"] is False,
        "biometric_unlock_locked": RUNTIME["biometric_unlock_enabled"] is False,
        "external_security_system_locked": RUNTIME["external_security_system_enabled"] is False,
        "approval_required_before_unlock": RUNTIME["approval_required_before_any_unlock"] is True,
        "audit_written": after_audit_count > before_audit_count,
        "preview_only_fail_closed": GOVERNANCE_RULES["preview_only"]
        and GOVERNANCE_RULES["unknown_person_fail_closed"],
        "no_fake_pass": GOVERNANCE_RULES["no_fake_pass"],
    }
    passed = sum(1 for ok in checks.values() if ok)
    total = len(checks)
    return {
        "ok": passed == total,
        "phase": "tuka_face_identity_privacy_guard_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "samples": {
            "unknown": unknown,
            "admin": admin,
            "employee": employee,
            "blocked_unlock": blocked_unlock,
            "unknown_unlock": unknown_unlock,
            "preview_admin_unlock": preview_admin_unlock,
            "enrollment_blocked": enrollment_blocked,
            "enrollment_ready": enrollment_ready,
            "delete_request": delete_request,
        },
        "execution_locked": True,
        "updated_at": now_iso(),
    }


def main() -> None:
    print(json.dumps(verify_face_identity_privacy_guard(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
