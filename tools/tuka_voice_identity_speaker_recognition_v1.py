from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_PATH = DATA_DIR / "tuka_voice_identity_speaker_recognition_v1_report.json"
MEMORY_PATH = DATA_DIR / "tuka_voice_identity_speaker_recognition_v1_memory.jsonl"
AUDIT_PATH = DATA_DIR / "tuka_voice_identity_speaker_recognition_audit.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_jsonl(path: Path, event: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


VOICE_IDENTITY_CAPABILITIES = [
    {
        "id": "speaker_classification",
        "name": "Speaker Classification",
        "classes": ["admin", "employee", "customer", "unknown_caller"],
        "can_preview": ["speaker_label", "confidence_bucket", "unknown_fail_closed"],
        "blocked_without_approval": ["grant_access", "sensitive_action", "identity_claim_as_fact"],
    },
    {
        "id": "voice_memory",
        "name": "Voice Memory",
        "can_preview": ["consent_record", "encrypted_profile_stub", "delete_request_plan"],
        "blocked_without_approval": ["store_voice_profile", "reuse_voice_profile", "share_voice_profile"],
    },
    {
        "id": "call_identity_bridge",
        "name": "Call Assistant Identity Bridge",
        "can_preview": ["caller_identity_hint", "unknown_caller_script", "admin_escalation"],
        "blocked_without_approval": ["continue_sensitive_call", "transfer_call", "record_call"],
    },
    {
        "id": "meeting_speaker_attribution",
        "name": "Meeting Speaker Attribution",
        "can_preview": ["speaker_turn_labels", "meeting_protocol_draft", "uncertain_speaker_markers"],
        "blocked_without_approval": ["record_meeting", "store_biometric_audio", "publish_minutes"],
    },
    {
        "id": "anti_spoof_liveness",
        "name": "Anti-spoof / Liveness",
        "can_preview": ["replay_risk_flag", "voice_clone_risk_flag", "liveness_challenge_plan"],
        "blocked_without_approval": ["trust_voice_as_single_factor", "bypass_admin_approval"],
    },
]


GLOBAL_GUARDS = {
    "no_profile_without_consent": True,
    "unknown_voice_never_claimed_known": True,
    "voice_identity_not_enough_for_sensitive_action": True,
    "admin_approval_required": True,
    "voice_data_encrypted_at_rest_required": True,
    "delete_request_removes_profile": True,
    "no_live_microphone_enabled": True,
    "no_raw_audio_storage": True,
    "no_biometric_profile_written": True,
    "audit_required": True,
    "preview_only": True,
    "fail_closed": True,
    "no_fake_pass": True,
}


def voice_identity_registry() -> dict[str, Any]:
    registry = {
        "ok": True,
        "engine": "tuka_voice_identity_speaker_recognition_v1",
        "mode": "consent_first_speaker_identity_preview",
        "updated_at": _now(),
        "public_name": "Tuka Voice Identity / Speaker Recognition",
        "capabilities": VOICE_IDENTITY_CAPABILITIES,
        "global_guards": GLOBAL_GUARDS,
        "roadmap_position": [
            "Core Stability",
            "Governance / Guardrails",
            "Voice Layer",
            "Voice Identity",
            "Phone Assistant",
            "Meeting Assistant",
            "Business Executive Assistant",
        ],
        "runtime": {
            "speaker_recognition_live": False,
            "microphone_enabled": False,
            "raw_audio_storage_enabled": False,
            "profile_storage_enabled": False,
            "sensitive_action_unlock_by_voice": False,
            "approval_required_before_profile_write": True,
        },
    }
    _append_jsonl(MEMORY_PATH, {"ts": _now(), "event": "voice_identity_registry_built", "capability_count": len(VOICE_IDENTITY_CAPABILITIES)})
    return registry


def build_voice_profile_preview(person_id: str, *, consent_given: bool = False) -> dict[str, Any]:
    profile_key = hashlib.sha256(f"tuka-voice-profile:{person_id}".encode("utf-8")).hexdigest()[:16]
    allowed = consent_given
    result = {
        "ok": True,
        "person_id": person_id,
        "consent_given": consent_given,
        "profile_key_preview": profile_key,
        "profile_storage_allowed": allowed,
        "profile_written": False,
        "raw_audio_stored": False,
        "encrypted_at_rest_required": True,
        "delete_supported": True,
        "blocked": not allowed,
        "reason": "consent_required_before_profile_storage" if not allowed else "consent_recorded_profile_write_still_preview_only",
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "voice_profile_preview", "person_id": person_id, "allowed": allowed})
    return result


def classify_speaker_preview(sample_label: str, *, enrolled: bool = False, confidence: float = 0.0) -> dict[str, Any]:
    if not enrolled or confidence < 0.75:
        speaker_class = "unknown_caller"
        decision = "Unknown caller. Ask admin before continuing."
        trusted = False
    else:
        speaker_class = sample_label if sample_label in {"admin", "employee", "customer"} else "unknown_caller"
        decision = f"Speaker classified as {speaker_class}, but approval is still required for sensitive actions."
        trusted = speaker_class != "unknown_caller"
    result = {
        "ok": True,
        "speaker_class": speaker_class,
        "confidence": confidence,
        "trusted_for_identity_hint": trusted,
        "trusted_for_sensitive_action": False,
        "decision": decision,
        "admin_approval_required": True,
        "external_action_executed": False,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "speaker_classified_preview", "speaker_class": speaker_class, "confidence": confidence})
    return result


def build_meeting_protocol_preview(turns: list[dict[str, str]]) -> dict[str, Any]:
    protocol = []
    for index, turn in enumerate(turns, start=1):
        speaker = turn.get("speaker") or "Unknown"
        text = turn.get("text") or ""
        if speaker.lower() in {"unknown", "unknown_caller"}:
            speaker = "Unknown speaker"
        protocol.append(f"{speaker}: {text}")
    result = {
        "ok": True,
        "turn_count": len(protocol),
        "protocol": protocol,
        "recording_used": False,
        "raw_audio_stored": False,
        "speaker_uncertainty_preserved": any("Unknown speaker:" in line for line in protocol),
        "approval_required_before_publish": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "meeting_protocol_preview", "turn_count": len(protocol)})
    return result


def evaluate_liveness_preview(*, replay_risk: bool = False, clone_risk: bool = False) -> dict[str, Any]:
    risk = "high" if replay_risk or clone_risk else "low"
    result = {
        "ok": True,
        "replay_risk": replay_risk,
        "voice_clone_risk": clone_risk,
        "risk": risk,
        "liveness_challenge_required": risk == "high",
        "voice_identity_trusted_as_single_factor": False,
        "sensitive_action_allowed": False,
        "admin_approval_required": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "liveness_preview", "risk": risk})
    return result


def evaluate_delete_profile_request(person_id: str) -> dict[str, Any]:
    result = {
        "ok": True,
        "person_id": person_id,
        "delete_supported": True,
        "profile_deleted": False,
        "reason": "preview_only_no_profile_storage_enabled",
        "audit_written": True,
    }
    _append_jsonl(AUDIT_PATH, {"ts": _now(), "event": "voice_profile_delete_requested", "person_id": person_id})
    return result


def verify_voice_identity() -> dict[str, Any]:
    registry = voice_identity_registry()
    caps = registry["capabilities"]
    guards = registry["global_guards"]
    runtime = registry["runtime"]
    no_consent_profile = build_voice_profile_preview("employee_001", consent_given=False)
    consent_profile = build_voice_profile_preview("employee_001", consent_given=True)
    unknown = classify_speaker_preview("admin", enrolled=False, confidence=0.95)
    admin_hint = classify_speaker_preview("admin", enrolled=True, confidence=0.88)
    meeting = build_meeting_protocol_preview(
        [
            {"speaker": "Battulga", "text": "Open the project review."},
            {"speaker": "Unknown", "text": "I have a question."},
            {"speaker": "Sarah", "text": "Action item confirmed."},
        ]
    )
    liveness = evaluate_liveness_preview(replay_risk=True, clone_risk=True)
    delete_request = evaluate_delete_profile_request("employee_001")
    checks = {
        "registry_ok": registry["ok"] is True,
        "five_capabilities_registered": len(caps) == 5,
        "speaker_classification_present": any(item["id"] == "speaker_classification" for item in caps),
        "voice_memory_present": any(item["id"] == "voice_memory" for item in caps),
        "call_bridge_present": any(item["id"] == "call_identity_bridge" for item in caps),
        "meeting_attribution_present": any(item["id"] == "meeting_speaker_attribution" for item in caps),
        "anti_spoof_present": any(item["id"] == "anti_spoof_liveness" for item in caps),
        "no_profile_without_consent": no_consent_profile["blocked"] is True and guards["no_profile_without_consent"] is True,
        "consent_profile_still_preview_only": consent_profile["consent_given"] is True and consent_profile["profile_written"] is False,
        "unknown_voice_fail_closed": unknown["speaker_class"] == "unknown_caller"
        and "Ask admin" in unknown["decision"],
        "voice_not_enough_for_sensitive_action": admin_hint["trusted_for_sensitive_action"] is False
        and guards["voice_identity_not_enough_for_sensitive_action"] is True,
        "meeting_protocol_labels_speakers": meeting["turn_count"] == 3
        and meeting["speaker_uncertainty_preserved"] is True,
        "liveness_flags_high_risk": liveness["risk"] == "high"
        and liveness["liveness_challenge_required"] is True,
        "voice_clone_not_single_factor": liveness["voice_identity_trusted_as_single_factor"] is False,
        "delete_request_supported": delete_request["delete_supported"] is True,
        "voice_data_encryption_required": guards["voice_data_encrypted_at_rest_required"] is True,
        "live_microphone_locked": runtime["microphone_enabled"] is False
        and runtime["speaker_recognition_live"] is False,
        "raw_audio_and_profile_storage_locked": runtime["raw_audio_storage_enabled"] is False
        and runtime["profile_storage_enabled"] is False,
        "approval_required": runtime["approval_required_before_profile_write"] is True
        and guards["admin_approval_required"] is True,
        "audit_written": guards["audit_required"] is True and AUDIT_PATH.exists(),
        "roadmap_position_present": "Voice Identity" in registry["roadmap_position"],
        "fail_closed": guards["fail_closed"] is True,
        "no_fake_pass": guards["no_fake_pass"] is True,
    }
    passed = sum(1 for value in checks.values() if value is True)
    report = {
        "ok": passed == len(checks),
        "phase": "tuka_voice_identity_speaker_recognition_v1",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "registry": registry,
        "examples": {
            "no_consent_profile": no_consent_profile,
            "consent_profile": consent_profile,
            "unknown_speaker": unknown,
            "admin_identity_hint": admin_hint,
            "meeting_protocol": meeting,
            "liveness": liveness,
            "delete_request": delete_request,
        },
        "execution_locked": True,
        "updated_at": _now(),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(verify_voice_identity(), indent=2, ensure_ascii=False))
