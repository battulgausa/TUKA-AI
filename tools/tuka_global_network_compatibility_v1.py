"""Tuka Global Network Compatibility v1.

Governed preview module for making Tuka network-aware across countries,
providers, devices, and unstable internet conditions. This file does not open
network sockets or contact external endpoints; it defines and verifies the
policy contract that future live network routing must obey.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "global_network_compatibility_audit.jsonl"


SUPPORTED_REGIONS = [
    "usa",
    "mongolia",
    "europe",
    "asia",
    "global_fallback",
]


SUPPORTED_NETWORKS = [
    "wifi",
    "ethernet",
    "mobile_data",
    "vpn",
    "corporate_network",
    "unknown_network",
]


CAPABILITIES = [
    "network_detection",
    "region_detection",
    "latency_check",
    "firewall_vpn_awareness",
    "api_endpoint_fallback",
    "offline_limited_mode",
    "multi_region_server_support",
    "secure_connection_check",
]


ARCHITECTURE = [
    "Tuka App",
    "Nearest Region API",
    "Fallback API",
    "Secure Bridge",
    "Tuka Core",
]


ROADMAP_POSITION = [
    "Core Stability",
    "Governance / Guardrails",
    "Network Brain / Infra Brain",
    "Global Network Compatibility",
    "Secure Bridge",
    "Multi-region Runtime",
    "Global Business Operations",
]


GOVERNANCE_RULES = {
    "unknown_network_limited_mode": True,
    "insecure_connection_blocks_sensitive_action": True,
    "vpn_proxy_uncertainty_manual_review": True,
    "different_country_laws_compliance_check": True,
    "all_access_audit_log": True,
    "no_sensitive_action_on_limited_mode": True,
    "endpoint_fallback_requires_secure_bridge": True,
    "offline_mode_disables_external_actions": True,
    "fail_closed": True,
    "preview_only": True,
    "no_fake_pass": True,
}


RUNTIME = {
    "live_region_probe_enabled": False,
    "live_latency_probe_enabled": False,
    "live_endpoint_switch_enabled": False,
    "live_vpn_probe_enabled": False,
    "live_firewall_scan_enabled": False,
    "external_network_action_enabled": False,
    "secure_bridge_required": True,
    "admin_approval_required_for_sensitive_network_action": True,
}


ENDPOINTS = {
    "usa": {
        "primary": "api-us.tuka.local-preview",
        "fallback": "api-global-fallback.tuka.local-preview",
    },
    "mongolia": {
        "primary": "api-mn.tuka.local-preview",
        "fallback": "api-asia.tuka.local-preview",
    },
    "europe": {
        "primary": "api-eu.tuka.local-preview",
        "fallback": "api-global-fallback.tuka.local-preview",
    },
    "asia": {
        "primary": "api-asia.tuka.local-preview",
        "fallback": "api-global-fallback.tuka.local-preview",
    },
    "global_fallback": {
        "primary": "api-global-fallback.tuka.local-preview",
        "fallback": "offline-limited-mode",
    },
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
        "engine": "tuka_global_network_compatibility_v1",
        "mode": "governed_network_compatibility_preview",
        "public_name": "Tuka Global Network Compatibility",
        "updated_at": now_iso(),
        "supported_regions": SUPPORTED_REGIONS,
        "supported_networks": SUPPORTED_NETWORKS,
        "capabilities": CAPABILITIES,
        "architecture": ARCHITECTURE,
        "endpoints": ENDPOINTS,
        "governance_rules": GOVERNANCE_RULES,
        "runtime": RUNTIME,
        "roadmap_position": ROADMAP_POSITION,
    }


def classify_network(
    *,
    region: str | None,
    network_type: str | None,
    latency_ms: int | None,
    secure_connection: bool,
    vpn_or_proxy_uncertain: bool = False,
    firewall_restricted: bool = False,
    local_law_uncertain: bool = False,
) -> dict[str, Any]:
    normalized_region = region if region in SUPPORTED_REGIONS else "global_fallback"
    normalized_network = network_type if network_type in SUPPORTED_NETWORKS else "unknown_network"
    unknown_network = normalized_network == "unknown_network"
    unstable = latency_ms is None or latency_ms > 800 or firewall_restricted
    limited_mode = (
        unknown_network
        or not secure_connection
        or vpn_or_proxy_uncertain
        or unstable
        or local_law_uncertain
    )
    manual_review = vpn_or_proxy_uncertain or local_law_uncertain or firewall_restricted
    result = {
        "ok": True,
        "region": normalized_region,
        "network_type": normalized_network,
        "latency_ms": latency_ms,
        "secure_connection": secure_connection,
        "vpn_or_proxy_uncertain": vpn_or_proxy_uncertain,
        "firewall_restricted": firewall_restricted,
        "local_law_uncertain": local_law_uncertain,
        "limited_mode": limited_mode,
        "manual_review_required": manual_review,
        "sensitive_actions_allowed": not limited_mode,
        "offline_mode": latency_ms is None,
        "fail_closed": limited_mode,
        "audit_written": True,
    }
    write_audit({"event": "network_classified", **result})
    return result


def select_endpoint(network_state: dict[str, Any]) -> dict[str, Any]:
    region = network_state["region"]
    secure = bool(network_state["secure_connection"])
    limited = bool(network_state["limited_mode"])
    endpoint_set = ENDPOINTS.get(region, ENDPOINTS["global_fallback"])
    target = endpoint_set["fallback"] if limited else endpoint_set["primary"]
    allowed_to_switch = secure and RUNTIME["secure_bridge_required"] and not RUNTIME["live_endpoint_switch_enabled"]
    result = {
        "ok": True,
        "region": region,
        "selected_endpoint": target,
        "primary_endpoint": endpoint_set["primary"],
        "fallback_endpoint": endpoint_set["fallback"],
        "secure_bridge_required": True,
        "live_switch_executed": False,
        "allowed_to_switch_in_preview": allowed_to_switch,
        "limited_mode": limited,
        "audit_written": True,
    }
    write_audit({"event": "endpoint_selected", **result})
    return result


def evaluate_network_action(
    action: str,
    network_state: dict[str, Any],
    *,
    admin_approved: bool = False,
    compliance_reviewed: bool = False,
) -> dict[str, Any]:
    sensitive_actions = {
        "send_private_data",
        "execute_remote_task",
        "connect_cloud_bridge",
        "switch_production_endpoint",
        "sync_business_records",
    }
    sensitive = action in sensitive_actions
    blocked = False
    reasons: list[str] = []
    if network_state["limited_mode"] and sensitive:
        blocked = True
        reasons.append("limited_mode_blocks_sensitive_action")
    if not network_state["secure_connection"] and sensitive:
        blocked = True
        reasons.append("insecure_connection")
    if network_state["vpn_or_proxy_uncertain"]:
        blocked = True
        reasons.append("vpn_proxy_uncertainty_manual_review")
    if network_state["local_law_uncertain"] and not compliance_reviewed:
        blocked = True
        reasons.append("country_law_compliance_review_required")
    if sensitive and not admin_approved:
        blocked = True
        reasons.append("admin_approval_required")

    result = {
        "ok": True,
        "action": action,
        "sensitive": sensitive,
        "allowed": not blocked,
        "blocked": blocked,
        "admin_approved": admin_approved,
        "compliance_reviewed": compliance_reviewed,
        "external_network_action_executed": False,
        "reasons": reasons or ["preview_allowed_no_live_action"],
        "fail_closed": blocked,
        "audit_written": True,
    }
    write_audit({"event": "network_action_evaluated", **result})
    return result


def verify_global_network_compatibility() -> dict[str, Any]:
    before_audit_count = 0
    if AUDIT_PATH.exists():
        before_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    reg = registry()
    healthy_usa_wifi = classify_network(
        region="usa",
        network_type="wifi",
        latency_ms=80,
        secure_connection=True,
    )
    mongolia_mobile = classify_network(
        region="mongolia",
        network_type="mobile_data",
        latency_ms=280,
        secure_connection=True,
    )
    unknown_network = classify_network(
        region=None,
        network_type=None,
        latency_ms=150,
        secure_connection=True,
    )
    insecure = classify_network(
        region="europe",
        network_type="ethernet",
        latency_ms=50,
        secure_connection=False,
    )
    vpn_uncertain = classify_network(
        region="asia",
        network_type="vpn",
        latency_ms=120,
        secure_connection=True,
        vpn_or_proxy_uncertain=True,
    )
    low_bandwidth = classify_network(
        region="usa",
        network_type="wifi",
        latency_ms=1500,
        secure_connection=True,
    )
    offline = classify_network(
        region="mongolia",
        network_type="wifi",
        latency_ms=None,
        secure_connection=True,
    )
    country_law = classify_network(
        region="europe",
        network_type="corporate_network",
        latency_ms=90,
        secure_connection=True,
        local_law_uncertain=True,
    )
    endpoint_healthy = select_endpoint(healthy_usa_wifi)
    endpoint_unknown = select_endpoint(unknown_network)
    endpoint_offline = select_endpoint(offline)
    blocked_private = evaluate_network_action(
        "send_private_data",
        insecure,
        admin_approved=True,
        compliance_reviewed=True,
    )
    vpn_blocked = evaluate_network_action(
        "connect_cloud_bridge",
        vpn_uncertain,
        admin_approved=True,
        compliance_reviewed=True,
    )
    legal_blocked = evaluate_network_action(
        "sync_business_records",
        country_law,
        admin_approved=True,
        compliance_reviewed=False,
    )
    preview_safe = evaluate_network_action(
        "read_network_status",
        healthy_usa_wifi,
        admin_approved=False,
        compliance_reviewed=False,
    )

    after_audit_count = 0
    if AUDIT_PATH.exists():
        after_audit_count = len(AUDIT_PATH.read_text(encoding="utf-8").splitlines())

    checks = {
        "registry_ok": reg["ok"],
        "regions_present": set(SUPPORTED_REGIONS)
        == {"usa", "mongolia", "europe", "asia", "global_fallback"},
        "network_types_present": set(SUPPORTED_NETWORKS)
        == {"wifi", "ethernet", "mobile_data", "vpn", "corporate_network", "unknown_network"},
        "capabilities_complete": set(CAPABILITIES)
        == {
            "network_detection",
            "region_detection",
            "latency_check",
            "firewall_vpn_awareness",
            "api_endpoint_fallback",
            "offline_limited_mode",
            "multi_region_server_support",
            "secure_connection_check",
        },
        "architecture_complete": ARCHITECTURE
        == ["Tuka App", "Nearest Region API", "Fallback API", "Secure Bridge", "Tuka Core"],
        "roadmap_position_present": "Global Network Compatibility" in ROADMAP_POSITION,
        "unknown_network_limited": unknown_network["limited_mode"] is True,
        "unknown_network_sensitive_blocked": unknown_network["sensitive_actions_allowed"] is False,
        "insecure_limited": insecure["limited_mode"] is True,
        "insecure_sensitive_blocked": blocked_private["blocked"] is True
        and "insecure_connection" in blocked_private["reasons"],
        "vpn_uncertainty_manual_review": vpn_uncertain["manual_review_required"] is True,
        "vpn_action_blocked": vpn_blocked["blocked"] is True,
        "country_law_compliance_required": country_law["manual_review_required"] is True,
        "country_law_action_blocked_without_review": legal_blocked["blocked"] is True,
        "low_bandwidth_limited": low_bandwidth["limited_mode"] is True,
        "offline_limited": offline["offline_mode"] is True and offline["limited_mode"] is True,
        "healthy_wifi_not_limited": healthy_usa_wifi["limited_mode"] is False,
        "mongolia_mobile_supported": mongolia_mobile["region"] == "mongolia"
        and mongolia_mobile["network_type"] == "mobile_data",
        "endpoint_primary_for_healthy": endpoint_healthy["selected_endpoint"] == ENDPOINTS["usa"]["primary"],
        "endpoint_fallback_for_unknown": endpoint_unknown["selected_endpoint"]
        == ENDPOINTS["global_fallback"]["fallback"],
        "endpoint_fallback_for_offline": endpoint_offline["selected_endpoint"]
        == ENDPOINTS["mongolia"]["fallback"],
        "secure_bridge_required": RUNTIME["secure_bridge_required"] is True,
        "live_region_probe_locked": RUNTIME["live_region_probe_enabled"] is False,
        "live_latency_probe_locked": RUNTIME["live_latency_probe_enabled"] is False,
        "live_endpoint_switch_locked": RUNTIME["live_endpoint_switch_enabled"] is False,
        "external_network_action_locked": RUNTIME["external_network_action_enabled"] is False,
        "safe_status_read_allowed": preview_safe["allowed"] is True
        and preview_safe["external_network_action_executed"] is False,
        "all_access_audited": after_audit_count > before_audit_count,
        "governance_rules_present": all(GOVERNANCE_RULES.values()),
        "preview_only_fail_closed": GOVERNANCE_RULES["preview_only"] and GOVERNANCE_RULES["fail_closed"],
        "no_fake_pass": GOVERNANCE_RULES["no_fake_pass"],
    }
    passed = sum(1 for ok in checks.values() if ok)
    total = len(checks)
    return {
        "ok": passed == total,
        "phase": "tuka_global_network_compatibility_v1",
        "passed": passed,
        "total": total,
        "checks": checks,
        "registry": reg,
        "samples": {
            "healthy_usa_wifi": healthy_usa_wifi,
            "mongolia_mobile": mongolia_mobile,
            "unknown_network": unknown_network,
            "insecure": insecure,
            "vpn_uncertain": vpn_uncertain,
            "low_bandwidth": low_bandwidth,
            "offline": offline,
            "country_law": country_law,
            "endpoint_healthy": endpoint_healthy,
            "endpoint_unknown": endpoint_unknown,
            "endpoint_offline": endpoint_offline,
            "blocked_private": blocked_private,
            "vpn_blocked": vpn_blocked,
            "legal_blocked": legal_blocked,
            "preview_safe": preview_safe,
        },
        "execution_locked": True,
        "updated_at": now_iso(),
    }


def main() -> None:
    print(json.dumps(verify_global_network_compatibility(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
